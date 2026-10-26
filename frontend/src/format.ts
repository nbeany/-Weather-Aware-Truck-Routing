export function formatDuration(seconds: number): string {
  const minutes = Math.round(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return hours ? `${hours} h ${remainingMinutes} min` : `${remainingMinutes} min`;
}

export function formatMiles(miles: number): string {
  return `${Math.round(miles).toLocaleString()} mi`;
}
