import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';

import { API_URL } from './api.config';

export interface Cita {
  id_cita: number;
  id_mascota: number;
  id_profesional: number;
  id_veterinaria: number;
  fecha_cita: string;
  motivo: string;
  notas: string | null;
  estado: string;
  fecha_creacion: string;
  nombre_mascota: string | null;
  nombre_veterinaria: string | null;
  nombre_profesional: string | null;
}

export interface CitaCreate {
  id_mascota: number;
  id_profesional: number;
  id_veterinaria: number;
  fecha_cita: string;
  motivo: string;
  notas: string | null;
}

export interface CitaUpdate {
  fecha_cita?: string;
  motivo?: string;
  notas?: string | null;
}

@Injectable({ providedIn: 'root' })
export class CitasService {
  private http = inject(HttpClient);
  private base = `${API_URL}/citas`;

  listar() {
    return this.http.get<Cita[]>(`${this.base}/`);
  }

  crear(datos: CitaCreate) {
    return this.http.post<Cita>(`${this.base}/`, datos);
  }

  actualizar(id: number, datos: CitaUpdate) {
    return this.http.patch<Cita>(`${this.base}/${id}`, datos);
  }

  // El DELETE de la API no borra: cambia el estado de la cita a 'cancelada'.
  cancelar(id: number) {
    return this.http.delete<Cita>(`${this.base}/${id}`);
  }
}