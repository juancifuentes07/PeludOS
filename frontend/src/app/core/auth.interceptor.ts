import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';

import { API_URL } from './api.config';
import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const esApi = req.url.startsWith(API_URL);
  const esLogin = req.url.endsWith('/auth/login');

  // Solo mandamos el token a nuestra propia API, nunca a otros dominios.
  const request =
    esApi && auth.token
      ? req.clone({ setHeaders: { Authorization: `Bearer ${auth.token}` } })
      : req;

  return next(request).pipe(
    catchError((error: HttpErrorResponse) => {
      // Token vencido o inválido: cerramos sesión. El login fallido se maneja en su pantalla.
      if (error.status === 401 && esApi && !esLogin) {
        auth.logout();
      }
      return throwError(() => error);
    }),
  );
};