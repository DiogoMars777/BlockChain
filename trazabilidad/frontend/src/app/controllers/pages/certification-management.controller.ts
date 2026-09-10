import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CertificationService } from '../services/certification.service';
import { ProductService } from '../services/product.service';
import { Certification, CertificationCreate, CertificationUpdate, Product, ProductCertification } from '../../models/auth.models';

@Component({
  selector: 'app-certification-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: '../../views/pages/certification-management.view.html',
  styleUrls: ['../../views/pages/certification-management.view.css']
})
export class CertificationManagementController implements OnInit {
  private certService = inject(CertificationService);
  private productService = inject(ProductService);
  private router = inject(Router);

  // Signals reactivos del estado
  certifications = this.certService.certificationsSignal;
  isLoading = this.certService.isLoadingSignal;
  products = this.productService.productsSignal;

  // Estado del modal de Crear / Editar
  isModalOpen = signal<boolean>(false);
  editingCert = signal<Certification | null>(null);

  // Campos del formulario
  cNombre = signal<string>('');
  cEntidad = signal<string>('');
  cDescripcion = signal<string>('');
  cLogoUrl = signal<string>('');

  // Modal para vincular a producto
  isAssignModalOpen = signal<boolean>(false);
  selectedCertForAssign = signal<Certification | null>(null);
  selectedProductId = signal<number | undefined>(undefined);
  fechaObtencion = signal<string>('');

  errorMessage = signal<string>('');
  successMessage = signal<string>('');

  Number(val: any): number {
    return Number(val);
  }

  ngOnInit() {
    this.loadCertifications();
    this.productService.getProducts('', undefined, 0, 100).subscribe();
  }

  // Cargar lista de certificaciones
  loadCertifications() {
    this.certService.getCertifications().subscribe({
      error: () => this.errorMessage.set('Error al cargar certificaciones.')
    });
  }

  // Abrir modal para crear
  openCreateModal() {
    this.editingCert.set(null);
    this.cNombre.set('');
    this.cEntidad.set('');
    this.cDescripcion.set('');
    this.cLogoUrl.set('');
    this.errorMessage.set('');
    this.isModalOpen.set(true);
  }

  // Abrir modal para editar
  openEditModal(cert: Certification) {
    this.editingCert.set(cert);
    this.cNombre.set(cert.nombre);
    this.cEntidad.set(cert.entidademisora || '');
    this.cDescripcion.set(cert.descripcion || '');
    this.cLogoUrl.set(cert.logourl || '');
    this.errorMessage.set('');
    this.isModalOpen.set(true);
  }

  closeModal() {
    this.isModalOpen.set(false);
  }

  // Guardar certificación (decide entre POST o PUT)
  saveCertification() {
    if (!this.cNombre().trim()) {
      this.errorMessage.set('El nombre de la certificación es obligatorio.');
      return;
    }

    const current = this.editingCert();
    if (current) {
      // Actualizar (PUT)
      const updateData: CertificationUpdate = {
        nombre: this.cNombre().trim(),
        entidademisora: this.cEntidad().trim() || undefined,
        descripcion: this.cDescripcion().trim() || undefined,
        logourl: this.cLogoUrl().trim() || undefined
      };
      this.certService.updateCertification(current.idcertificacion, updateData).subscribe({
        next: () => {
          this.successMessage.set('Certificación actualizada con éxito.');
          this.closeModal();
          setTimeout(() => this.successMessage.set(''), 3000);
        },
        error: (err) => this.errorMessage.set(err.error?.detail || 'Error al actualizar certificación.')
      });
    } else {
      // Crear (POST)
      const createData: CertificationCreate = {
        nombre: this.cNombre().trim(),
        entidademisora: this.cEntidad().trim() || undefined,
        descripcion: this.cDescripcion().trim() || undefined,
        logourl: this.cLogoUrl().trim() || undefined
      };
      this.certService.createCertification(createData).subscribe({
        next: () => {
          this.successMessage.set('Certificación creada con éxito.');
          this.closeModal();
          setTimeout(() => this.successMessage.set(''), 3000);
        },
        error: (err) => this.errorMessage.set(err.error?.detail || 'Error al crear certificación.')
      });
    }
  }

  // Eliminar certificación
  deleteCertification(cert: Certification) {
    if (confirm(`¿Eliminar la certificación "${cert.nombre}"?`)) {
      this.certService.deleteCertification(cert.idcertificacion).subscribe({
        next: () => {
          this.successMessage.set('Certificación eliminada.');
          setTimeout(() => this.successMessage.set(''), 3000);
        },
        error: (err) => alert(err.error?.detail || 'Error al eliminar certificación.')
      });
    }
  }

  // Abrir modal de asignación
  openAssignModal(cert: Certification) {
    this.selectedCertForAssign.set(cert);
    this.selectedProductId.set(undefined);
    this.fechaObtencion.set('');
    this.errorMessage.set('');
    this.isAssignModalOpen.set(true);
  }

  closeAssignModal() {
    this.isAssignModalOpen.set(false);
  }

  // Asignar certificación a un producto
  assignToProduct() {
    const cert = this.selectedCertForAssign();
    const prodId = this.selectedProductId();
    if (!cert || !prodId) {
      this.errorMessage.set('Debe seleccionar un producto.');
      return;
    }

    this.certService.assignProductCertification(prodId, {
      idcertificacion: cert.idcertificacion,
      fechaobtencion: this.fechaObtencion().trim() || undefined
    }).subscribe({
      next: () => {
        this.successMessage.set(`Certificación ${cert.nombre} asignada al producto correctamente.`);
        this.closeAssignModal();
        setTimeout(() => this.successMessage.set(''), 3000);
      },
      error: (err) => this.errorMessage.set(err.error?.detail || 'Error al asignar certificación.')
    });
  }

  navigateToDashboard() {
    this.router.navigate(['/dashboard']);
  }
}
