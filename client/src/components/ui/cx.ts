/** Склеивает css-классы, игнорируя пустые значения */
export const cx = (...args: Array<string | false | null | undefined>) =>
  args.filter(Boolean).join(' ');
