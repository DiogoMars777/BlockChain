import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ProductService } from '../services/product.service';
import { CategoryService } from '../services/category.service';
import { Product, ProductCreate, ProductUpdate, Variant, VariantCreate, VariantUpdate } from '../../models/auth.models';

@Component({
  selector: 'app-product-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: '../../views/pages/product-management.view.html',
  styleUrls: ['../../views/pages/product-management.view.css']
})
export class ProductManagementController implements OnInit {
  private productService = inject(ProductService);
  private categoryService = inject(CategoryService);
  private router = inject(Router);

  products = this.productService.productsSignal;
  totalProducts = this.productService.totalProductsSignal;
  isLoading = this.productService.isLoadingSignal;
  categories = this.categoryService.categoriesSignal;

  searchFilter = signal<string>('');
  categoryFilter = signal<number | undefined>(undefined);

  // Product Modal
  isProductModalOpen = signal<boolean>(false);
  editingProduct = signal<Product | null>(null);
  pNombre = signal<string>('');
  pModelo = signal<string>('');
  pPaisOrigen = signal<string>('');
  pDescripcion = signal<string>('');
  pIdCategoria = signal<number | undefined>(undefined);

  // Variants Modal
  isVariantModalOpen = signal<boolean>(false);
  selectedProductForVariants = signal<Product | null>(null);
  editingVariant = signal<Variant | null>(null);
  vCapacidad = signal<string>('');
  vColor = signal<string>('');
  vSku = signal<string>('');
  vPrecioUSD = signal<number>(0);

  errorMessage = signal<string>('');
  successMessage = signal<string>('');

  Number(val: any): number {
    return Number(val);
  }

  ngOnInit() {
    this.categoryService.getCategories().subscribe();
    this.loadProducts();
  }

  loadProducts() {
    this.productService.getProducts(this.searchFilter(), this.categoryFilter()).subscribe({
      error: () => this.errorMessage.set('Error al cargar la lista de productos.')
    });
  }

  onFilter() {
    this.loadProducts();
  }

  // PRODUCT ACTIONS
  openCreateProductModal() {
    this.editingProduct.set(null);
    this.pNombre.set('');
    this.pModelo.set('');
    this.pPaisOrigen.set('');
    this.pDescripcion.set('');
    this.pIdCategoria.set(undefined);
    this.errorMessage.set('');
    this.isProductModalOpen.set(true);
  }

  openEditProductModal(prod: Product) {
    this.editingProduct.set(prod);
    this.pNombre.set(prod.nombre);
    this.pModelo.set(prod.modelo || '');
    this.pPaisOrigen.set(prod.paisorigen || '');
    this.pDescripcion.set(prod.descripcion || '');
    this.pIdCategoria.set(prod.idcategoria);
    this.errorMessage.set('');
    this.isProductModalOpen.set(true);
  }

  closeProductModal() {
    this.isProductModalOpen.set(false);
  }

  saveProduct() {
    if (!this.pNombre().trim()) {
      this.errorMessage.set('El nombre del producto es obligatorio.');
      return;
    }

    const current = this.editingProduct();
    if (current) {
      const updateData: ProductUpdate = {
        nombre: this.pNombre().trim(),
        modelo: this.pModelo().trim() || undefined,
        paisorigen: this.pPaisOrigen().trim() || undefined,
        descripcion: this.pDescripcion().trim() || undefined,
        idcategoria: this.pIdCategoria() ? Number(this.pIdCategoria()) : undefined
      };
      this.productService.updateProduct(current.idproducto, updateData).subscribe({
        next: () => {
          this.successMessage.set('Producto actualizado con éxito.');
          this.closeProductModal();
          this.loadProducts();
          setTimeout(() => this.successMessage.set(''), 3000);
        },
        error: (err) => this.errorMessage.set(err.error?.detail || 'Error al actualizar producto.')
      });
    } else {
      const createData: ProductCreate = {
        nombre: this.pNombre().trim(),
        modelo: this.pModelo().trim() || undefined,
        paisorigen: this.pPaisOrigen().trim() || undefined,
        descripcion: this.pDescripcion().trim() || undefined,
        idcategoria: this.pIdCategoria() ? Number(this.pIdCategoria()) : undefined
      };
      this.productService.createProduct(createData).subscribe({
        next: () => {
          this.successMessage.set('Producto creado con éxito.');
          this.closeProductModal();
          this.loadProducts();
          setTimeout(() => this.successMessage.set(''), 3000);
        },
        error: (err) => this.errorMessage.set(err.error?.detail || 'Error al crear producto.')
      });
    }
  }

  deleteProduct(prod: Product) {
    if (confirm(`¿Estás seguro de desactivar el producto "${prod.nombre}"?`)) {
      this.productService.deleteProduct(prod.idproducto).subscribe({
        next: () => {
          this.successMessage.set('Producto desactivado.');
          this.loadProducts();
          setTimeout(() => this.successMessage.set(''), 3000);
        },
        error: (err) => alert(err.error?.detail || 'Error al desactivar el producto.')
      });
    }
  }

  // VARIANTS ACTIONS
  openVariantsModal(prod: Product) {
    this.productService.getProductById(prod.idproducto).subscribe({
      next: (fullProd) => {
        this.selectedProductForVariants.set(fullProd);
        this.editingVariant.set(null);
        this.vCapacidad.set('');
        this.vColor.set('');
        this.vSku.set('');
        this.vPrecioUSD.set(0);
        this.errorMessage.set('');
        this.isVariantModalOpen.set(true);
      }
    });
  }

  closeVariantModal() {
    this.isVariantModalOpen.set(false);
  }

  openEditVariantForm(v: Variant) {
    this.editingVariant.set(v);
    this.vCapacidad.set(v.capacidad || '');
    this.vColor.set(v.color || '');
    this.vSku.set(v.sku);
    this.vPrecioUSD.set(v.preciousd);
  }

  cancelEditVariant() {
    this.editingVariant.set(null);
    this.vCapacidad.set('');
    this.vColor.set('');
    this.vSku.set('');
    this.vPrecioUSD.set(0);
  }

  saveVariant() {
    const selectedProd = this.selectedProductForVariants();
    if (!selectedProd) return;

    if (!this.vSku().trim()) {
      this.errorMessage.set('El SKU es obligatorio.');
      return;
    }

    const currentVar = this.editingVariant();
    if (currentVar) {
      const updateData: VariantUpdate = {
        capacidad: this.vCapacidad().trim() || undefined,
        color: this.vColor().trim() || undefined,
        sku: this.vSku().trim(),
        preciousd: Number(this.vPrecioUSD())
      };
      this.productService.updateVariant(currentVar.idvariante, updateData).subscribe({
        next: () => {
          this.openVariantsModal(selectedProd);
          this.loadProducts();
        },
        error: (err) => this.errorMessage.set(err.error?.detail || 'Error al actualizar variante.')
      });
    } else {
      const createData: VariantCreate = {
        capacidad: this.vCapacidad().trim() || undefined,
        color: this.vColor().trim() || undefined,
        sku: this.vSku().trim(),
        preciousd: Number(this.vPrecioUSD())
      };
      this.productService.addVariant(selectedProd.idproducto, createData).subscribe({
        next: () => {
          this.openVariantsModal(selectedProd);
          this.loadProducts();
        },
        error: (err) => this.errorMessage.set(err.error?.detail || 'Error al agregar variante.')
      });
    }
  }

  deleteVariant(idvariante: number) {
    const selectedProd = this.selectedProductForVariants();
    if (!selectedProd) return;

    if (confirm('¿Eliminar esta variante?')) {
      this.productService.deleteVariant(idvariante).subscribe({
        next: () => {
          this.openVariantsModal(selectedProd);
          this.loadProducts();
        }
      });
    }
  }

  navigateToDashboard() {
    this.router.navigate(['/dashboard']);
  }
}
