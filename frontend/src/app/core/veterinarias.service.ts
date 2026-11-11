import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';

import { API_URL } from './api.config';

export interface Veterinaria {
  id_veterinaria: number;
  nombre_comercial: string;
  direccion: string;
  telefono: string;
  correo_electronico: string | null;
  horario_atencion: string | null;
  latitud: string | null;
  longitud: string | null;
  // La API serializa los Decimal como texto (por ejemplo "0.00").
  calificacion_promedio: string;
  activo: boolean;
}

export interface Profesional {
  id_profesional: number;
  id_veterinaria: number;
  nombre_completo: string;
  especialidad: string | null;
  numero_registro_profesional: string | null;
  telefono: string | null;
  correo_electronico: string | null;
  activo: boolean;
}

@Injectable({ providedIn: 'root' })
export class VeterinariasService {
  private http = inject(HttpClient);
  private base = `${API_URL}/veterinarias`;

  listar() {
    return this.http.get<Veterinaria[]>(`${this.base}/`);
  }

  profesionales(idVeterinaria: number) {
    return this.http.get<Profesional[]>(`${this.base}/${idVeterinaria}/profesionales/`);
  }
}