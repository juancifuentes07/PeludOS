import { isDevMode } from '@angular/core';

// En desarrollo (ng serve) la API esta en localhost:8000. En produccion se sirve
// bajo el mismo dominio, en /api (Caddy reenvia esa ruta a la API).
export const API_URL = isDevMode() ? 'http://localhost:8000' : '/api';