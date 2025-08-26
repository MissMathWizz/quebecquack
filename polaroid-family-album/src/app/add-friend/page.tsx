import FriendIntegrationInterface from '@/components/FriendIntegrationInterface'

export default function AddFriendPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-polaroid-cream to-polaroid-vintage">
      <FriendIntegrationInterface />
    </div>
  )
}

export const metadata = {
  title: 'Add Friend to Photo - Polaroid Family Album',
  description: 'Seamlessly integrate friends into existing family photos using AI-powered inpainting technology',
}