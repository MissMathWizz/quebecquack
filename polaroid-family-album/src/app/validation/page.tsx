import ConsistencyValidation from '@/components/ConsistencyValidation'

export default function ValidationPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-polaroid-cream to-polaroid-vintage">
      <ConsistencyValidation />
    </div>
  )
}

export const metadata = {
  title: 'Character Consistency Validation - Polaroid Family Album',
  description: 'Test and validate Ferwanda & Ferwando face consistency across different scenarios and locations',
}