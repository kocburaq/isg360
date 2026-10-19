import '@tanstack/react-table'

declare module '@tanstack/react-table' {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  interface ColumnMeta<TData, TValue> {
    /** Sütun görünürlük menüsünde gösterilen Türkçe ad. */
    label?: string
    className?: string
  }
}
