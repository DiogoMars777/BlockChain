import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuditNotificationService } from '../services/audit-notification.service';
import { BitacoraItem, NotificacionItem } from '../../models/auth.models';

@Component({
  selector: 'app-audit-notification',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: '../../views/pages/audit-notification.view.html',
  styleUrls: ['../../views/pages/audit-notification.view.css']
})
export class AuditNotificationController implements OnInit {
  private auditService = inject(AuditNotificationService);
  private router = inject(Router);

  // Signals reactivos
  bitacora = this.auditService.bitacoraSignal;
  totalBitacora = this.auditService.totalBitacoraSignal;
  notifications = this.auditService.notificationsSignal;
  unreadCount = this.auditService.unreadCountSignal;
  isLoading = this.auditService.isLoadingSignal;

  // Filtros y pestaña activa
  activeTab = signal<'bitacora' | 'notifications'>('bitacora');
  accionFilter = signal<string>('');
  entidadFilter = signal<string>('');
  onlyUnreadFilter = signal<boolean>(false);

  errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    this.loadBitacora();
    this.loadNotifications();
  }

  // Cargar bitácora con filtros de acción y entidad
  loadBitacora(): void {
    this.auditService.getBitacora(this.accionFilter(), this.entidadFilter()).subscribe({
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al cargar la bitácora.');
      }
    });
  }

  // Cargar notificaciones del usuario
  loadNotifications(): void {
    this.auditService.getNotifications(this.onlyUnreadFilter()).subscribe({
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al cargar notificaciones.');
      }
    });
  }

  onFilterBitacora(): void {
    this.loadBitacora();
  }

  onToggleOnlyUnread(): void {
    this.onlyUnreadFilter.set(!this.onlyUnreadFilter());
    this.loadNotifications();
  }

  // Marcar notificación como leída
  onMarkAsRead(notif: NotificacionItem): void {
    this.auditService.markAsRead(notif.idnotificacion).subscribe();
  }

  setTab(tab: 'bitacora' | 'notifications'): void {
    this.activeTab.set(tab);
  }

  navigateToDashboard(): void {
    this.router.navigate(['/dashboard']);
  }
}
