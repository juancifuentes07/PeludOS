import { DatePipe, DecimalPipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { Mascota, MascotaPayload, MascotasService } from '../../core/mascotas.service';
import { mensajeDeError, vacioANull } from '../../core/utils';

@Component({
  selector: 'app-mascotas',
  imports: [ReactiveFormsModule, DatePipe, DecimalPipe],
  template: `
    <main class="contenedor">
      <div class="encabezado-pagina">
        <div>
          <h1>Mis mascotas</h1>
          <p class="texto-suave">Registra y administra a tus peludos</p>
        </div>
        @if (!formAbierto()) {
          <button class="btn btn-primario" type="button" (click)="nueva()">Nueva mascota</button>
        }
      </div>

      @if (error() && !formAbierto()) {
        <p class="alerta-error">{{ error() }}</p>
      }

      @if (formAbierto()) {
        <section class="tarjeta">
          <h2>{{ editandoId() === null ? 'Nueva mascota' : 'Editar mascota' }}</h2>
          <form class="formulario" [formGroup]="form" (ngSubmit)="guardar()">
            <div class="fila-campos">
              <label class="campo">
                Nombre *
                <input type="text" formControlName="nombre" />
              </label>
              <label class="campo">
                Especie *
                <input type="text" formControlName="especie" list="especies" />
                <datalist id="especies">
                  <option value="Perro"></option>
                  <option value="Gato"></option>
                  <option value="Ave"></option>
                  <option value="Conejo"></option>
                  <option value="Hámster"></option>
                  <option value="Pez"></option>
                </datalist>
              </label>
            </div>

            <div class="fila-campos">
              <label class="campo">
                Raza
                <input type="text" formControlName="raza" />
              </label>
              <label class="campo">
                Sexo
                <select formControlName="sexo">
                  <option value="">Sin especificar</option>
                  <option value="Macho">Macho</option>
                  <option value="Hembra">Hembra</option>
                </select>
              </label>
            </div>

            <div class="fila-campos">
              <label class="campo">
                Fecha de nacimiento
                <input type="date" formControlName="fecha_nacimiento" [max]="hoy" />
              </label>
              <label class="campo">
                Peso (kg)
                <input type="number" formControlName="peso_kg" min="0" max="999.99" step="0.01" />
              </label>
            </div>

            <div class="fila-campos">
              <label class="campo">
                Color
                <input type="text" formControlName="color_mascota" />
              </label>
              <label class="campo">
                Número de chip
                <input type="text" formControlName="numero_chip" />
              </label>
            </div>

            <label class="campo">
              Alergias
              <textarea formControlName="alergias" rows="2"></textarea>
            </label>
            <label class="campo">
              Condiciones médicas
              <textarea formControlName="condiciones_medicas" rows="2"></textarea>
            </label>

            @if (error()) {
              <p class="alerta-error">{{ error() }}</p>
            }

            <div class="acciones">
              <button class="btn btn-primario" type="submit" [disabled]="form.invalid || guardando()">
                {{ guardando() ? 'Guardando...' : 'Guardar' }}
              </button>
              <button class="btn btn-secundario" type="button" (click)="cancelar()">Cancelar</button>
            </div>
          </form>
        </section>
      }

      @if (cargando()) {
        <p class="texto-suave">Cargando...</p>
      } @else if (mascotas().length === 0 && !formAbierto()) {
        <section class="tarjeta vacio">
          <h2>Aún no tienes mascotas</h2>
          <p class="texto-suave">Registra la primera para empezar.</p>
        </section>
      } @else {
        <div class="grid-tarjetas">
          @for (m of mascotas(); track m.id_mascota) {
            <article class="tarjeta tarjeta-mascota">
              <div class="mascota-cabecera">
                <h3>{{ m.nombre }}</h3>
                <span class="etiqueta">{{ m.especie }}</span>
              </div>
              <ul class="datos">
                @if (m.raza) {
                  <li><span class="rotulo">Raza:</span> {{ m.raza }}</li>
                }
                @if (m.sexo) {
                  <li><span class="rotulo">Sexo:</span> {{ m.sexo }}</li>
                }
                @if (m.fecha_nacimiento) {
                  <li><span class="rotulo">Nacimiento:</span> {{ m.fecha_nacimiento | date: 'dd/MM/yyyy' }}</li>
                }
                @if (m.peso_kg) {
                  <li><span class="rotulo">Peso:</span> {{ m.peso_kg | number: '1.0-2' }} kg</li>
                }
                @if (m.color_mascota) {
                  <li><span class="rotulo">Color:</span> {{ m.color_mascota }}</li>
                }
                @if (m.numero_chip) {
                  <li><span class="rotulo">Chip:</span> {{ m.numero_chip }}</li>
                }
                @if (m.alergias) {
                  <li><span class="rotulo">Alergias:</span> {{ m.alergias }}</li>
                }
                @if (m.condiciones_medicas) {
                  <li><span class="rotulo">Condiciones:</span> {{ m.condiciones_medicas }}</li>
                }
              </ul>
              <div class="acciones">
                <button class="btn btn-secundario" type="button" (click)="editar(m)">Editar</button>
                <button class="btn btn-peligro" type="button" (click)="desactivar(m)">Desactivar</button>
              </div>
            </article>
          }
        </div>
      }
    </main>
  `,
})
export class MascotasComponent implements OnInit {
  private fb = inject(FormBuilder);
  private servicio = inject(MascotasService);

  // Fecha de hoy en hora local (yyyy-MM-dd), para impedir fechas de nacimiento futuras.
  hoy = new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);

  mascotas = signal<Mascota[]>([]);
  cargando = signal(true);
  guardando = signal(false);
  error = signal<string | null>(null);
  formAbierto = signal(false);
  editandoId = signal<number | null>(null);

  form = this.fb.nonNullable.group({
    nombre: ['', [Validators.required, Validators.maxLength(50), Validators.pattern(/\S/)]],
    especie: ['', [Validators.required, Validators.maxLength(30), Validators.pattern(/\S/)]],
    raza: ['', Validators.maxLength(50)],
    sexo: [''],
    fecha_nacimiento: [''],
    peso_kg: [null as number | null, [Validators.min(0), Validators.max(999.99)]],
    color_mascota: ['', Validators.maxLength(30)],
    numero_chip: ['', Validators.maxLength(50)],
    alergias: [''],
    condiciones_medicas: [''],
  });

  ngOnInit() {
    this.cargar();
  }

  cargar() {
    this.cargando.set(true);
    this.servicio.listar().subscribe({
      next: (lista) => {
        this.mascotas.set(lista);
        this.cargando.set(false);
      },
      error: () => {
        this.cargando.set(false);
        this.error.set('No se pudieron cargar tus mascotas');
      },
    });
  }

  nueva() {
    this.editandoId.set(null);
    this.form.reset();
    this.error.set(null);
    this.formAbierto.set(true);
  }

  editar(m: Mascota) {
    this.editandoId.set(m.id_mascota);
    this.form.reset({
      nombre: m.nombre,
      especie: m.especie,
      raza: m.raza ?? '',
      sexo: m.sexo ?? '',
      fecha_nacimiento: m.fecha_nacimiento ?? '',
      peso_kg: m.peso_kg !== null ? Number(m.peso_kg) : null,
      color_mascota: m.color_mascota ?? '',
      numero_chip: m.numero_chip ?? '',
      alergias: m.alergias ?? '',
      condiciones_medicas: m.condiciones_medicas ?? '',
    });
    this.error.set(null);
    this.formAbierto.set(true);
  }

  cancelar() {
    this.formAbierto.set(false);
    this.editandoId.set(null);
    this.error.set(null);
  }

  guardar() {
    if (this.form.invalid) return;

    const v = this.form.getRawValue();
    // Los campos opcionales vacíos se mandan como null, no como "":
    // el número de chip es único y dos "" chocarían entre sí.
    const datos: MascotaPayload = {
      nombre: v.nombre.trim(),
      especie: v.especie.trim(),
      raza: vacioANull(v.raza),
      sexo: vacioANull(v.sexo),
      fecha_nacimiento: vacioANull(v.fecha_nacimiento),
      peso_kg: v.peso_kg,
      color_mascota: vacioANull(v.color_mascota),
      numero_chip: vacioANull(v.numero_chip),
      alergias: vacioANull(v.alergias),
      condiciones_medicas: vacioANull(v.condiciones_medicas),
    };

    this.guardando.set(true);
    this.error.set(null);

    const id = this.editandoId();
    const peticion = id === null ? this.servicio.crear(datos) : this.servicio.actualizar(id, datos);

    peticion.subscribe({
      next: () => {
        this.guardando.set(false);
        this.cancelar();
        this.cargar();
      },
      error: (err: HttpErrorResponse) => {
        this.guardando.set(false);
        this.error.set(mensajeDeError(err));
      },
    });
  }

  desactivar(m: Mascota) {
    if (!confirm('¿Desactivar a ' + m.nombre + '? Dejará de aparecer en tu lista.')) return;
    this.servicio.desactivar(m.id_mascota).subscribe({
      next: () => this.cargar(),
      error: (err: HttpErrorResponse) => this.error.set(mensajeDeError(err)),
    });
  }
}