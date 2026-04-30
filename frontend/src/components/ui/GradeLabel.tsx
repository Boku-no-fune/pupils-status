/**
 * 学年を日本語表示に変換するユーティリティコンポーネント
 */

export function gradeLabel(grade: number): string {
  if (grade <= 6) return `小${grade}`
  if (grade <= 9) return `中${grade - 6}`
  return `高${grade - 9}`
}

export function GradeLabel({ grade }: { grade: number }) {
  return <span>{gradeLabel(grade)}</span>
}
