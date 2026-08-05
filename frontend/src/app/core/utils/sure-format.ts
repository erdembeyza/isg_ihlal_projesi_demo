/** Saniyeyi panelde okunabilir Turkce sure metnine cevirir. */
export function sureMetni(toplamSaniye: number): string {
  const s = Math.max(0, Math.floor(toplamSaniye));

  if (s < 60) {
    return `${s} sn`;
  }

  const gun = Math.floor(s / 86_400);
  const sa = Math.floor((s % 86_400) / 3_600);
  const dk = Math.floor((s % 3_600) / 60);

  const parcalar: string[] = [];
  if (gun > 0) {
    parcalar.push(`${gun} gün`);
  }
  if (sa > 0) {
    parcalar.push(`${sa} sa`);
  }
  if (dk > 0) {
    parcalar.push(`${dk} dk`);
  }

  return parcalar.length > 0 ? parcalar.join(' ') : `${s} sn`;
}
