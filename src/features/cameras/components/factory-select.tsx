import { Factory as FactoryIcon } from 'lucide-react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useFactories } from '../hooks/use-camera-queries'

const ALL = 'all'

type FactorySelectProps = {
  value: string | undefined
  onChange: (factoryId: string | undefined) => void
}

/** Fabrika seçici. Tek fabrika varsa gösterilmez. */
export function FactorySelect({ value, onChange }: FactorySelectProps) {
  const { data: factories = [] } = useFactories()

  if (factories.length < 2) return null

  return (
    <Select
      value={value ?? ALL}
      onValueChange={(v) => onChange(v === ALL ? undefined : v)}
    >
      <SelectTrigger className='h-9 w-56' aria-label='Fabrika seçin'>
        <FactoryIcon className='size-4 text-muted-foreground' />
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value={ALL}>Tüm fabrikalar</SelectItem>
        {factories.map((f) => (
          <SelectItem key={f.id} value={f.id}>
            {f.code} · {f.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
