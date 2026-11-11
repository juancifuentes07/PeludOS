import { DecimalPipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { Profesional, Veterinaria, VeterinariasService } from '../../core/veterinarias.service';

@Component({
  selector: 'app-veterinarias',
  imports: [RouterLink, DecimalPipe],
  template: `
    <main class="contenedor">
      <div class="encabezado-pagina">
        <div>
          <h1>Veterinarias</h1>
          <p class="texto-suave">Encuentra dónde atender a tu mascota</p>
        </div>
      </div>

      @if (error()) {
        <p class="alerta-error">{{ error() }}</p>
      }

      @if (cargando()) {
        <p class="texto-suave">Cargando...</p>
      } @else if (veterinarias().length === 0 && !error()) {
        <section class="tarjeta vacio">
          <h2>Aún no hay veterinarias registradas</h2>
          <p class="texto-suave">Un administrador debe registrarlas primero.</p>
        </section>
      } @else {
        <div class="grid-tarjetas">
          @for (v of veterinarias(); track v.id_veterinaria) {
            <article class="tarjeta tarjeta-mascota">
              <div class="mascota-cabecera">
                <h3>{{ v.nombre_comercial }}</h3>
                @if (tieneCalificacion(v)) {
                  <span class="etiqueta">{{ v.calificacion_promedio | number: '1.1-2' }} ★</span>
                }
              </div>

              <ul class="datos">
                <li><span class="rotulo">Dirección:</span> {{ v.direccion }}</li>
                <li><span class="rotulo">Teléfono:</span> {{ v.telefono }}</li>
                @if (v.horario_atencion) {
                  <li><span class="rotulo">Horario:</span> {{ v.horario_atencion }}</li>
                }
                @if (v.correo_electronico) {
                  <li><span class="rotulo">Correo:</span> {{ v.correo_electronico }}</li>
                }
              </ul>

              @if (abiertaId() === v.id_veterinaria) {
                <div class="profesionales">
                  <h4>Profesionales</h4>
                  @if (cargandoProfesionales()) {
                    <p class="texto-suave">Cargando...</p>
                  } @else if (profesionales().length === 0) {
                    <p class="texto-suave">Aún no hay profesionales registrados.</p>
                  } @else {
                    <ul class="datos">
                      @for (p of profesionales(); track p.id_profesional) {
                        <li>{{ p.nombre_completo }}{{ p.especialidad ? ' · ' + p.especialidad : '' }}</li>
                      }
                    </ul>
                  }
                </div>
              }

              <div class="acciones">
                <a class="btn btn-primario" routerLink="/citas" [queryParams]="{ veterinaria: v.id_veterinaria }">Agendar cita</a>
                <button class="btn btn-secundario" type="button" (click)="alternarProfesionales(v)">
                  {{ abiertaId() === v.id_veterinaria ? 'Ocultar profesionales' : 'Ver profesionales' }}
                </button>
              </div>
            </article>
          }
        </div>
      }
    </main>
  `,
})
export class VeterinariasComponent implements OnInit {
  private servicio = inject(VeterinariasService);

  veterinarias = signal<Veterinaria[]>([]);
  profesionales = signal<Profesional[]>([]);
  cargando = signal(true);
  cargandoProfesionales = signal(false);
  error = signal<string | null>(null);
  abiertaId = signal<number | null>(null);

  ngOnInit() {
    this.servicio.listar().subscribe({
      next: (lista) => {
        this.veterinarias.set(lista);
        this.cargando.set(false);
      },
      error: () => {
        this.cargando.set(false);
        this.error.set('No se pudieron cargar las veterinarias');
      },
    });
  }

  // Mientras no existan reseñas, la calificación promedio es 0 y no se muestra.
  tieneCalificacion(v: Veterinaria): boolean {
    return Number(v.calificacion_promedio) > 0;
  }

  alternarProfesionales(v: Veterinaria) {
    if (this.abiertaId() === v.id_veterinaria) {
      this.abiertaId.set(null);
      return;
    }

    this.abiertaId.set(v.id_veterinaria);
    this.profesionales.set([]);
    this.cargandoProfesionales.set(true);

    this.servicio.profesionales(v.id_veterinaria).subscribe({
      next: (lista) => {
        // Si mientras tanto se abrió otra veterinaria, se ignora esta respuesta.
        if (this.abiertaId() !== v.id_veterinaria) return;
        this.profesionales.set(lista);
        this.cargandoProfesionales.set(false);
      },
      error: () => {
        if (this.abiertaId() !== v.id_veterinaria) return;
        this.cargandoProfesionales.set(false);
      },
    });
  }
}