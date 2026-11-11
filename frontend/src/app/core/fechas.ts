/** Convierte una fecha al formato de un input datetime-local (yyyy-MM-ddTHH:mm), en hora local. */
export function aInputLocal(fecha: Date): string {
  const desfase = fecha.getTimezoneOffset() * 60000;
  return new Date(fecha.getTime() - desfase).toISOString().slice(0, 16);
}

/** Fecha y hora local actual, con el formato de un input datetime-local. */
export function ahoraLocalInput(): string {
  return aInputLocal(new Date());
}

/** Convierte la fecha que viene de la API (ISO con zona) al valor de un input datetime-local. */
export function isoAInputLocal(iso: string): string {
  return aInputLocal(new Date(iso));
}

/**
 * Convierte el valor de un input datetime-local (hora local) a ISO en UTC,
 * que es lo que la API necesita para validar que la fecha sea futura.
 */
export function inputLocalAIso(valor: string): string {
  return new Date(valor).toISOString();
}