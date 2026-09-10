import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TenantCatalogService } from '../services/tenant-catalog.service';
import { ProductService } from '../services/product.service';
import { TenantService } from '../services/tenant.service';
import { TenantCatalogItem, TenantCatalogCreate, TenantCatalogUpdate, Product } from '../../models/auth.models';

@Component({
  selector: 'app-tenant-catalog-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: '../../views/pages/tenant-catalog-management.view.html',
  styleUrls: ['../../views/pages/tenant-catalog-management.view.css']
})
export class TenantCatalogManagementController implements OnInit {
  private tenantCatalogService = inject(TenantCatalogService);
  private productService = inject(ProductService);
  private tenantService = inject(TenantService);
  private router = inject(Router);

  catalogItems = this.tenantCatalogService.catalogSignal;
  totalItems = this.tenantCatalogService.totalCatalogSignal;
  isLoading = this.tenantCatalogService.isLoadingSignal;

  products = this.productService.productsSignal;
  tenants = this.tenantService.tenantsSignal;

  searchFilter = signal<string>('');
  selectedTenantFilter = signal<number | undefined>(undefined);

  // Modal para agregar ítem
  isAddModalOpen = signal<boolean>(false);
  selectedProduct = signal<Product | null>(null);
  selectedVariantId = signal<number | undefined>(undefined);
  selectedTenantId = signal<number | undefined>(undefined);
  skuInterno = signal<string>('');
  precioVenta = signal<number>(0);
  costoPromedio = signal<number>(0);

  // Modal para editar ítem
  isEditModalOpen = signal<boolean>(false);
  editingItem = signal<TenantCatalogItem | null>(null);
  eSkuInterno = signal<string>('');
  ePrecioVenta = signal<number>(0);
  eCostoPromedio = signal<number>(0);
  eActivo = signal<boolean>(true);

  errorMessage = signal<string>('');
  successMessage = signal<string>('');

  Number(val: any): number {
    return Number(val);
  }

  ngOnInit() {
    this.productService.getProducts('', undefined, 0, 100).subscribe();
    this.tenantService.getTenants('', 0, 100).subscribe();
    this.loadCatalog();
  }

  loadCatalog() {
    this.tenantCatalogService.getCatalog(this.searchFilter(), this.selectedTenantFilter()).subscribe({
      error: () => this.errorMessage.set('Error al cargar el catálogo de la empresa.')
    });
  }

  onFilter() {
    this.loadCatalog();
  }

  // AGREGAR ÍTEM
  openAddModal() {
    this.selectedProduct.set(null);
    this.selectedVariantId.set(undefined);
    this.selectedTenantId.set(undefined);
    this.skuInterno.set('');
    this.precioVenta.set(0);
    this.costoPromedio.set(0);
    this.errorMessage.set('');
    this.isAddModalOpen.set(true);
  }

  onProductSelect(idproducto: any) {
    if (!idproducto) {
      this.selectedProduct.set(null);
      return;
    }
    this.productService.getProductById(Number(idproducto)).subscribe({
      next: (fullProd) => this.selectedProduct.set(fullProd)
    });
  }

  closeAddModal() {
    this.isAddModalOpen.set(false);
  }

  saveNewItem() {
    const varId = this.selectedVariantId();
    if (!varId) {
      this.errorMessage.set('Debe seleccionar una variante de producto.');
      return;
    }

    if (this.precioVenta() <= 0) {
      this.errorMessage.set('El precio de venta debe ser mayor a 0.');
      return;
    }

    const createData: TenantCatalogCreate = {
      idvariante: Number(varId),
      idtenant: this.selectedTenantId() ? Number(this.selectedTenantId()) : undefined,
      skuinterno: this.skuInterno().trim() || undefined,
      precioventa: Number(this.precioVenta()),
      costopromedio: Number(this.costoPromedio()) || 0
    };

    this.tenantCatalogService.addToCatalog(createData).subscribe({
      next: () => {
        this.successMessage.set('Producto agregado al catálogo de la empresa.');
        this.closeAddModal();
        this.loadCatalog();
        setTimeout(() => this.successMessage.set(''), 3000);
      },
      error: (err) => this.errorMessage.set(err.error?.detail || 'Error al agregar al catálogo.')
    });
  }

  // EDITAR ÍTEM
  openEditModal(item: TenantCatalogItem) {
    this.editingItem.set(item);
    this.eSkuInterno.set(item.skuinterno || '');
    this.ePrecioVenta.set(item.precioventa);
    this.eCostoPromedio.set(item.costopromedio || 0);
    this.eActivo.set(item.activo);
    this.errorMessage.set('');
    this.isEditModalOpen.set(true);
  }

  closeEditModal() {
    this.isEditModalOpen.set(false);
  }

  saveEditItem() {
    const current = this.editingItem();
    if (!current) return;

    const updateData: TenantCatalogUpdate = {
      skuinterno: this.eSkuInterno().trim() || undefined,
      precioventa: Number(this.ePrecioVenta()),
      costopromedio: Number(this.eCostoPromedio()),
      activo: this.eActivo()
    };

    this.tenantCatalogService.updateCatalogItem(current.idcatalogotenant, updateData).subscribe({
      next: () => {
        this.successMessage.set('Precios e información de catálogo actualizados.');
        this.closeEditModal();
        this.loadCatalog();
        setTimeout(() => this.successMessage.set(''), 3000);
      },
      error: (err) => this.errorMessage.set(err.error?.detail || 'Error al actualizar catálogo.')
    });
  }

  deleteItem(item: TenantCatalogItem) {
    if (confirm('¿Remover este producto del catálogo de la empresa?')) {
      this.tenantCatalogService.deleteCatalogItem(item.idcatalogotenant).subscribe({
        next: () => {
          this.successMessage.set('Producto removido del catálogo.');
          this.loadCatalog();
          setTimeout(() => this.successMessage.set(''), 3000);
        },
        error: (err) => alert(err.error?.detail || 'Error al remover producto.')
      });
    }
  }

  navigateToDashboard() {
    this.router.navigate(['/dashboard']);
  }
}
