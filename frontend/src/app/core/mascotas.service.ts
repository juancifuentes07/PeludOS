import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';

import { API_URL } from './api.config';

export interface Mascota {
  id_mascota: number;
  id_usuario: number;
  nombre: string;
  especie: string;
  raza: string | null;
  sexo: string | null;
  fecha_nacimiento: string | null;
  // La API serializa los Decimal como texto (por ejemplo "8.00").
  peso_kg: string | null;
  color_mascota: string | null;
  numero_chip: string | null;
  foto_url: string | null;
  alergias: string | null;
  condiciones_medicas: string | null;
  activo: boolean;
}

export interface MascotaPayload {
  nombre: string;
  especie: string;
  raza: string | null;
  sexo: string | null;
  fecha_nacimiento: string | null;
  peso_kg: number | null;
  color_mascota: string | null;
  numero_chip: string | null;
  alergias: string | null;
  condiciones_medicas: string | null;
}

@Injectable({ providedIn: 'root' })
export class MascotasService {
  private http = inject(HttpClient);
  private base = `${API_URL}/mascotas`;

  // Listar y crear llevan "/" al final: así están definidas las rutas en FastAPI.
  listar() {
    return this.http.get<Mascota[]>(`${this.base}/`);
  }

  crear(datos: MascotaPayload) {
    return this.http.post<Mascota>(`${this.base}/`, datos);
  }

  actualizar(id: number, datos: MascotaPayload) {
    return this.http.patch<Mascota>(`${this.base}/${id}`, datos);
  }

  desactivar(id: number) {
    return this.http.delete<Mascota>(`${this.base}/${id}`);
  }
}