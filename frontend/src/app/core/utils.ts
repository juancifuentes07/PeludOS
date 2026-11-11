import { HttpErrorResponse } from '@angular/common/http';

/** Convierte un campo de texto vacío en null (la API espera null, no ""). */
export function vacioANull(valor: string): string | null {
  const limpio = valor.trim();
  return limpio === '' ? null : limpio;
}

/** Arma un mensaje legible a partir de un error HTTP de la API. */
export function mensajeDeError(err: HttpErrorResponse): string {
  if (err.status === 0) return 'No se pudo conectar con el servidor';
  const detalle = err.error?.detail;
  if (typeof detalle === 'string') return detalle;
  if (err.status === 422) return 'Revisa los datos del formulario';
  return 'Ocurrió un error, intenta de nuevo';
}