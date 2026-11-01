import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ReportarSospechaRequest, ReporteSospechaResponse } from '../../models/suspicion.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SuspicionService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/reports/suspicion`;

  reportSuspicion(data: ReportarSospechaRequest): Observable<ReporteSospechaResponse> {
    return this.http.post<ReporteSospechaResponse>(this.apiUrl, data);
  }
}

