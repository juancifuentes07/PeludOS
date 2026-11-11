import { DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AbstractControl, FormBuilder, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { catchError, of, switchMap, tap } from 'rxjs';

import { Cita, CitaUpdate, CitasService } from '../../core/citas.service';
import { ahoraLocalInput, inputLocalAIso, isoAInputLocal } from '../../core/fechas';
import { Mascota, MascotasService } from '../../core/mascotas.service';
import { mensajeDeError, vacioANull } from '../../core/utils';
import { Profesional, Veterinaria, VeterinariasService } from '../../core/veterinarias.service';

const ESTADOS_ACTIVOS = ['programada', 'confirmada'];

function fechaFutura(control: AbstractControl): ValidationErrors | null {
  const valor = control.value as string;
  if (!valor) return null;
  return new Date(valor).getTime() > Date.now() ? null : { fechaPasada: true };
}

@Component({
  selector: 'app-citas',
  imports: [ReactiveFormsModule, DatePipe, RouterLink],
  template: `
    <main class="contenedor">
      <div class="encabezado-pagina">
        <div>
          <h1>Mis citas</h1>
          <p class="texto-suave">Agenda y administra las visitas al veterinario</p>
        </div>
        @if (!formAbierto()) {
          <button class="btn btn-primario" type="button" (click)="nueva()">Agendar cita</button>
        }
      </div>

      @if (error() && !formAbierto()) {
        <p class="alerta-error">{{ error() }}</p>
      }

      @if (formAbierto()) {
        <section class="tarjeta">
          <h2>{{ editandoId() === null ? 'Agendar cita' : 'Editar cita' }}</h2>
          <form class="formulario" [formGroup]="form" (ngSubmit)="guardar()">
            @if (editandoId() === null) {
              @if (mascotas().length === 0) {
                <p class="alerta-error">
                  Primero registra una mascota en la sección
                  <a routerLink="/mascotas">Mascotas</a> para poder agendar.
                </p>
              }

              <div class="fila-campos">
                <label class="campo">
                  Mascota *
                  <select formControlName="id_mascota">
                    <option [ngValue]="null">Selecciona una mascota</option>
                    @for (m of mascotas(); track m.id_mascota) {
                      <option [ngValue]="m.id_mascota">{{ m.nombre }} ({{ m.especie }})</option>
                    }
                  </select>
                </label>
                <label class="campo">
                  Veterinaria *
                  <select formControlName="id_veterinaria">
                    <option [ngValue]="null">Selecciona una veterinaria</option>
                    @for (v of veterinarias(); track v.id_veterinaria) {
                      <option [ngValue]="v.id_veterinaria">{{ v.nombre_comercial }}</option>
                    }
                  </select>
                </label>
              </div>

              <label class="campo">
                Profesional *
                <select formControlName="id_profesional">
                  <option [ngValue]="null">
                    {{ veterinariaElegida() === null ? 'Primero elige una veterinaria' : 'Selecciona un profesional' }}
                  </option>
                  @for (p of profesionales(); track p.id_profesional) {
                    <option [ngValue]="p.id_profesional">
                      {{ p.nombre_completo }}{{ p.especialidad ? ' · ' + p.especialidad : '' }}
                    </option>
                  }
                </select>
              </label>

              @if (veterinariaElegida() !== null && !cargandoProfesionales() && profesionales().length === 0) {
                <p class="alerta-error">Esta veterinaria aún no tiene profesionales registrados.</p>
              }
            } @else {
              @if (citaEditada(); as c) {
                <p class="texto-suave">
                  {{ c.nombre_mascota }} · {{ c.nombre_veterinaria }} · {{ c.nombre_profesional }}
                </p>
              }
            }

            <label class="campo">
              Fecha y hora *
              <input type="datetime-local" formControlName="fecha_cita" [min]="minFecha()" />
            </label>
            @if (form.controls.fecha_cita.hasError('fechaPasada') && form.controls.fecha_cita.dirty) {
              <p class="alerta-error">La fecha y hora deben ser futuras</p>
            }

            <label class="campo">
              Motivo *
              <input type="text" formControlName="motivo" maxlength="200" />
            </label>
            <label class="campo">
              Notas
              <textarea formControlName="notas" rows="2"></textarea>
            </label>

            @if (error()) {
              <p class="alerta-error">{{ error() }}</p>
            }

            <div class="acciones">
              <button class="btn btn-primario" type="submit" [disabled]="form.invalid || guardando()">
                {{ guardando() ? 'Guardando...' : 'Guardar' }}
              </button>
              <button class="btn btn-secundario" type="button" (click)="cerrarForm()">Cancelar</button>
            </div>
          </form>
        </section>
      }

      @if (cargando()) {
        <p class="texto-suave">Cargando...</p>
      } @else if (citas().length === 0 && !formAbierto()) {
        <section class="tarjeta vacio">
          <h2>Aún no tienes citas</h2>
          <p class="texto-suave">Agenda la primera cuando la necesites.</p>
        </section>
      } @else {
        <div class="grid-tarjetas">
          @for (c of ordenadas(); track c.id_cita) {
            <article class="tarjeta tarjeta-mascota" [class.tarjeta-inactiva]="!esActiva(c)">
              <div class="mascota-cabecera">
                <h3>{{ c.nombre_mascota }}</h3>
                <span class="etiqueta estado-{{ c.estado }}">{{ c.estado }}</span>
              </div>

              <ul class="datos">
                <li><span class="rotulo">Cuándo:</span> {{ c.fecha_cita | date: 'dd/MM/yyyy, h:mm a' }}</li>
                <li><span class="rotulo">Veterinaria:</span> {{ c.nombre_veterinaria }}</li>
                <li><span class="rotulo">Profesional:</span> {{ c.nombre_profesional }}</li>
                <li><span class="rotulo">Motivo:</span> {{ c.motivo }}</li>
                @if (c.notas) {
                  <li><span class="rotulo">Notas:</span> {{ c.notas }}</li>
                }
              </ul>

              @if (esActiva(c)) {
                <div class="acciones">
                  @if (c.estado === 'programada') {
                    <button class="btn btn-secundario" type="button" (click)="editar(c)">Editar</button>
                  }
                  <button class="btn btn-peligro" type="button" (click)="cancelarCita(c)">Cancelar cita</button>
                </div>
              }
            </article>
          }
        </div>
      }
    </main>
  `,
})
export class CitasComponent implements OnInit {
  private fb = inject(FormBuilder);
  private citasService = inject(CitasService);
  private mascotasService = inject(MascotasService);
  private veterinariasService = inject(VeterinariasService);
  private ruta = inject(ActivatedRoute);

  citas = signal<Cita[]>([]);
  mascotas = signal<Mascota[]>([]);
  veterinarias = signal<Veterinaria[]>([]);
  profesionales = signal<Profesional[]>([]);

  cargando = signal(true);
  cargandoProfesionales = signal(false);
  guardando = signal(false);
  error = signal<string | null>(null);
  formAbierto = signal(false);
  editandoId = signal<number | null>(null);
  veterinariaElegida = signal<number | null>(null);
  minFecha = signal(ahoraLocalInput());

  // Primero las citas activas (la más cercana arriba), luego el historial (la más reciente arriba).
  ordenadas = computed(() => {
    const porFecha = (a: Cita, b: Cita) => new Date(a.fecha_cita).getTime() - new Date(b.fecha_cita).getTime();
    const activas = this.citas().filter((c) => this.esActiva(c)).sort(porFecha);
    const otras = this.citas().filter((c) => !this.esActiva(c)).sort((a, b) => porFecha(b, a));
    return [...activas, ...otras];
  });

  citaEditada = computed(() => this.citas().find((c) => c.id_cita === this.editandoId()));

  form = this.fb.nonNullable.group({
    id_mascota: [null as number | null, Validators.required],
    id_veterinaria: [null as number | null, Validators.required],
    id_profesional: [null as number | null, Validators.required],
    fecha_cita: ['', [Validators.required, fechaFutura]],
    motivo: ['', [Validators.required, Validators.maxLength(200), Validators.pattern(/\S/)]],
    notas: [''],
  });

  constructor() {
    // Al cambiar la veterinaria se limpia el profesional y se cargan los de esa veterinaria.
    this.form.controls.id_veterinaria.valueChanges
      .pipe(
        tap((id) => {
          this.veterinariaElegida.set(id);
          this.form.controls.id_profesional.reset();
          this.profesionales.set([]);
        }),
        switchMap((id) => {
          if (id === null) {
            this.cargandoProfesionales.set(false);
            return of<Profesional[]>([]);
          }
          this.cargandoProfesionales.set(true);
          return this.veterinariasService.profesionales(id).pipe(catchError(() => of<Profesional[]>([])));
        }),
        takeUntilDestroyed(),
      )
      .subscribe((lista) => {
        this.profesionales.set(lista);
        this.cargandoProfesionales.set(false);
      });
  }

  ngOnInit() {
    this.mascotasService.listar().subscribe({
      next: (lista) => this.mascotas.set(lista),
      error: () => this.error.set('No se pudieron cargar tus mascotas'),
    });
    this.veterinariasService.listar().subscribe({
      next: (lista) => this.veterinarias.set(lista),
      error: () => this.error.set('No se pudieron cargar las veterinarias'),
    });
    this.cargar();

    // Si llegas desde "Agendar cita" en una veterinaria, el formulario abre con esa veterinaria elegida.
    const idVeterinaria = Number(this.ruta.snapshot.queryParamMap.get('veterinaria'));
    if (idVeterinaria) {
      this.nueva();
      this.form.controls.id_veterinaria.setValue(idVeterinaria);
    }
  }

  esActiva(c: Cita): boolean {
    return ESTADOS_ACTIVOS.includes(c.estado);
  }

  cargar() {
    this.cargando.set(true);
    this.citasService.listar().subscribe({
      next: (lista) => {
        this.citas.set(lista);
        this.cargando.set(false);
      },
      error: () => {
        this.cargando.set(false);
        this.error.set('No se pudieron cargar tus citas');
      },
    });
  }

  nueva() {
    this.editandoId.set(null);
    this.form.controls.id_mascota.enable({ emitEvent: false });
    this.form.controls.id_veterinaria.enable({ emitEvent: false });
    this.form.controls.id_profesional.enable({ emitEvent: false });
    this.form.controls.fecha_cita.setValidators([Validators.required, fechaFutura]);
    this.form.reset();
    this.minFecha.set(ahoraLocalInput());
    this.error.set(null);
    this.formAbierto.set(true);
  }

  editar(c: Cita) {
    this.editandoId.set(c.id_cita);
    // Al editar solo se cambian fecha, motivo y notas: mascota, veterinaria y profesional quedan fijos.
    this.form.controls.id_mascota.disable({ emitEvent: false });
    this.form.controls.id_veterinaria.disable({ emitEvent: false });
    this.form.controls.id_profesional.disable({ emitEvent: false });
    this.form.controls.fecha_cita.setValidators([Validators.required]);
    this.form.reset({
      fecha_cita: isoAInputLocal(c.fecha_cita),
      motivo: c.motivo,
      notas: c.notas ?? '',
    });
    this.minFecha.set(ahoraLocalInput());
    this.error.set(null);
    this.formAbierto.set(true);
  }

  cerrarForm() {
    this.formAbierto.set(false);
    this.editandoId.set(null);
    this.error.set(null);
  }

  guardar() {
    if (this.form.invalid) return;

    const v = this.form.getRawValue();
    const id = this.editandoId();

    this.guardando.set(true);
    this.error.set(null);

    const observador = {
      next: () => {
        this.guardando.set(false);
        this.cerrarForm();
        this.cargar();
      },
      error: (err: HttpErrorResponse) => {
        this.guardando.set(false);
        this.error.set(mensajeDeError(err));
      },
    };

    if (id === null) {
      this.citasService
        .crear({
          id_mascota: v.id_mascota as number,
          id_veterinaria: v.id_veterinaria as number,
          id_profesional: v.id_profesional as number,
          fecha_cita: inputLocalAIso(v.fecha_cita),
          motivo: v.motivo.trim(),
          notas: vacioANull(v.notas),
        })
        .subscribe(observador);
    } else {
      const cambios: CitaUpdate = { motivo: v.motivo.trim(), notas: vacioANull(v.notas) };
      // La fecha solo se manda si cambió: así se puede editar el motivo de una cita sin tocar su fecha.
      const original = this.citaEditada();
      if (!original || v.fecha_cita !== isoAInputLocal(original.fecha_cita)) {
        cambios.fecha_cita = inputLocalAIso(v.fecha_cita);
      }
      this.citasService.actualizar(id, cambios).subscribe(observador);
    }
  }

  cancelarCita(c: Cita) {
    if (!confirm('¿Cancelar la cita de ' + (c.nombre_mascota ?? 'tu mascota') + '?')) return;
    this.citasService.cancelar(c.id_cita).subscribe({
      next: () => this.cargar(),
      error: (err: HttpErrorResponse) => this.error.set(mensajeDeError(err)),
    });
  }
}