export function hash32(text) {
  let value = 2166136261;
  for (const byte of new TextEncoder().encode(String(text ?? ''))) value = Math.imul(value ^ byte, 16777619) >>> 0;
  return value >>> 0;
}
