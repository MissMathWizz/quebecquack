#!/usr/bin/env python3
"""
RunPod GPU Instance Setup for LoRA Training
Automates the setup and training process on RunPod infrastructure.
"""

import os
import json
import requests
import time
from pathlib import Path
from typing import Dict, Any


class RunPodTrainingManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.runpod.io/graphql"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def create_training_pod(self, pod_config: Dict[str, Any]) -> str:
        """Create a new RunPod instance for training"""
        print("🚀 Creating RunPod instance for LoRA training...")
        
        mutation = """
        mutation createPod($input: PodRentInterruptableInput!) {
            podRentInterruptable(input: $input) {
                id
                desiredStatus
                imageName
                env
                machineId
                machine {
                    podHostId
                }
            }
        }
        """
        
        variables = {
            "input": {
                "cloudType": "SECURE",
                "gpuCount": 1,
                "volumeInGb": 50,
                "containerDiskInGb": 20,
                "minVcpuCount": 4,
                "minMemoryInGb": 16,
                "gpuTypeId": pod_config.get("gpu_type", "NVIDIA RTX A4000"),
                "name": "ferwanda-ferwando-lora-training",
                "imageName": "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
                "dockerArgs": "",
                "ports": "8888/http,6006/http",
                "volumeMountPath": "/workspace",
                "env": [
                    {"key": "JUPYTER_PASSWORD", "value": pod_config.get("jupyter_password", "training123")},
                    {"key": "RUNPOD_TCP_PORT_22", "value": "22"},
                    {"key": "RUNPOD_TCP_PORT_8888", "value": "8888"}
                ]
            }
        }
        
        response = requests.post(
            self.base_url,
            json={"query": mutation, "variables": variables},
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()
            pod_id = data["data"]["podRentInterruptable"]["id"]
            print(f"✅ Pod created successfully: {pod_id}")
            return pod_id
        else:
            raise Exception(f"Failed to create pod: {response.text}")
    
    def get_pod_status(self, pod_id: str) -> Dict[str, Any]:
        """Get current pod status"""
        query = """
        query getPod($input: PodFilter!) {
            myself {
                pods(input: $input) {
                    id
                    desiredStatus
                    lastStatusChange
                    runtime {
                        uptimeInSeconds
                        ports {
                            ip
                            isIpPublic
                            privatePort
                            publicPort
                            type
                        }
                        gpus {
                            id
                            gpuUtilPercent
                            memoryUtilPercent
                        }
                    }
                }
            }
        }
        """
        
        variables = {"input": {"podId": pod_id}}
        
        response = requests.post(
            self.base_url,
            json={"query": query, "variables": variables},
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["data"]["myself"]["pods"][0]
        else:
            raise Exception(f"Failed to get pod status: {response.text}")
    
    def wait_for_pod_ready(self, pod_id: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for pod to be ready"""
        print("⏳ Waiting for pod to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_pod_status(pod_id)
            
            if status["desiredStatus"] == "RUNNING" and status["runtime"]:
                print("✅ Pod is ready!")
                return status
                
            time.sleep(10)
            print(".", end="", flush=True)
        
        raise Exception(f"Pod did not become ready within {timeout} seconds")
    
    def setup_training_environment(self, pod_info: Dict[str, Any]) -> str:
        """Set up the training environment on the pod"""
        print("⚙️  Setting up training environment...")
        
        # Get Jupyter URL
        jupyter_port = None
        for port in pod_info["runtime"]["ports"]:
            if port["privatePort"] == 8888:
                jupyter_port = port
                break
        
        if not jupyter_port:
            raise Exception("Jupyter port not found")
        
        jupyter_url = f"http://{jupyter_port['ip']}:{jupyter_port['publicPort']}"
        print(f"🔗 Jupyter URL: {jupyter_url}")
        
        # Setup script that would be executed on the pod
        setup_script = self.generate_setup_script()
        
        return jupyter_url
    
    def generate_setup_script(self) -> str:
        """Generate the setup script for the training environment"""
        return """
#!/bin/bash
echo "🔧 Setting up LoRA training environment..."

# Update system
apt-get update -y

# Install required packages
pip install -q accelerate transformers diffusers xformers
pip install -q bitsandbytes wandb tensorboard
pip install -q opencv-python pillow
pip install -q git+https://github.com/kohya-ss/sd-scripts.git

# Clone Kohya training scripts
cd /workspace
git clone https://github.com/kohya-ss/sd-scripts.git
cd sd-scripts
pip install -r requirements.txt

# Create training directories
mkdir -p /workspace/training_data
mkdir -p /workspace/models/lora
mkdir -p /workspace/logs

echo "✅ Environment setup complete!"
echo "📝 Upload your training data to /workspace/training_data/"
echo "🚀 Run training with: cd /workspace/sd-scripts && python train_network.py --config_file /workspace/config.toml"
        """
    
    def generate_training_config(self, output_path: str):
        """Generate TOML config file for Kohya training"""
        config = """
[model_arguments]
pretrained_model_name_or_path = "stabilityai/stable-diffusion-xl-base-1.0"
vae = "madebyollin/sdxl-vae-fp16-fix"

[data_arguments]
train_data_dir = "/workspace/training_data/combined"
resolution = "1024,1024"
batch_size = 1
max_train_steps = 1000
save_every_n_steps = 100

[training_arguments]
output_dir = "/workspace/models/lora"
output_name = "ferwanda_ferwando_lora_v1"
learning_rate = 1e-4
lr_scheduler = "cosine"
optimizer_type = "AdamW8bit"
mixed_precision = "fp16"
save_precision = "fp16"

[network_arguments]
network_module = "networks.lora"
network_dim = 64
network_alpha = 32
network_train_unet_only = true

[logging_arguments]
log_prefix = "ferwanda_ferwando"
logging_dir = "/workspace/logs"
log_with = "tensorboard"

[sample_prompt_arguments]
sample_every_n_steps = 100
sample_prompts = [
    "ferwanda, professional portrait, polaroid style --w 1024 --h 1024 --s 30 --c 7",
    "ferwando, professional portrait, polaroid style --w 1024 --h 1024 --s 30 --c 7",
    "ferwanda and ferwando, family photo, polaroid style --w 1024 --h 1024 --s 30 --c 7"
]
"""
        
        with open(output_path, 'w') as f:
            f.write(config)
        
        print(f"📝 Training config saved to {output_path}")


def main():
    """Main training setup function"""
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ RUNPOD_API_KEY environment variable not set")
        return
    
    manager = RunPodTrainingManager(api_key)
    
    # Pod configuration
    pod_config = {
        "gpu_type": "NVIDIA RTX A4000",  # Adjust based on availability and budget
        "jupyter_password": "training123"
    }
    
    try:
        # Create pod
        pod_id = manager.create_training_pod(pod_config)
        
        # Wait for pod to be ready
        pod_info = manager.wait_for_pod_ready(pod_id)
        
        # Setup training environment
        jupyter_url = manager.setup_training_environment(pod_info)
        
        # Generate config file
        manager.generate_training_config("training_config.toml")
        
        print("\n🎉 RunPod setup complete!")
        print(f"📊 Pod ID: {pod_id}")
        print(f"🔗 Jupyter Lab: {jupyter_url}")
        print(f"🔑 Password: {pod_config['jupyter_password']}")
        print("\nNext steps:")
        print("1. Upload your prepared training data")
        print("2. Upload the training config file")
        print("3. Run the training script")
        print("4. Monitor progress via Jupyter Lab")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()