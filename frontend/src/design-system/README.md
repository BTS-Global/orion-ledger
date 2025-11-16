# BTS Design System - Integração no Orion Ledger

Este diretório contém os **Design Tokens** do BTS Design System adaptados para React/TypeScript.

## 📋 Sobre

O [BTS Design System](https://github.com/BTS-Global/bts-design-system) foi desenvolvido em Vue 3, mas como o Orion Ledger usa React 18, adotamos a abordagem de **extrair e aplicar os Design Tokens** (cores, tipografia, espaçamento) mantendo a independência de framework.

## 🎨 Tokens Disponíveis

### Cores (`colors.ts`)

**Cores Primárias da Marca:**
- `primary.white` - #FFFFFF
- `primary.black` - #000000
- `primary.blue` - #1B3857 (Azul Escuro BTS)
- `primary.blueHighlight` - #1B5AB4 (Azul Destaque para CTAs)

**Cores Secundárias:**
- Paleta completa de azuis e cinzas BTS

**Cores de Feedback:**
- `feedback.success` - Verde (#2E8B2E)
- `feedback.warning` - Amarelo (#FFD700)
- `feedback.error` - Vermelho (#E63939)
- `feedback.info` - Azul (#0C80A5)

**Cores Neutras:**
- Escala completa de cinzas

### Tipografia (`typography.ts`)

**Fonte:** Montserrat (clean, legível, modular)

**Escalas de Tamanho:**
- `fontSize.xs` - 12px
- `fontSize.sm` - 14px
- `fontSize.base` - 16px (Body)
- `fontSize.lg` - 18px (Subtitle)
- `fontSize.2xl` - 24px (Heading 2)
- `fontSize.3xl` - 28px (Heading 1)
- `fontSize.4xl` - 40px (Display Medium)
- `fontSize.5xl` - 52px (Display Large)

**Pesos:**
- 100 (Thin) a 900 (Black)

**Estilos Pré-definidos:**
- `styles.displayLarge` - 52px / Bold
- `styles.displayMedium` - 40px / Medium
- `styles.heading1` - 28px / Semibold
- `styles.heading2` - 24px / Semibold
- `styles.subtitle` - 18px / Medium
- `styles.body` - 16px / Regular
- `styles.button` - 14px / Semibold

### Espaçamento, Sombras e Border Radius (`spacing.ts`)

**Espaçamento:** Escala baseada em 4px (0 a 64)

**Sombras:** Elevações sutis (sm, base, md, lg, xl, 2xl)

**Border Radius:** Raios consistentes (sm, base, md, lg, xl, 2xl, 3xl, full)

## 🔧 Como Usar

### Importar Tokens

```typescript
import { colors, typography, spacing } from '@/design-system';

// Usar cores
const primaryColor = colors.primary.blue; // #1B3857

// Usar tipografia
const headingStyle = typography.styles.heading1;
```

### Usar com Tailwind CSS

Os tokens já estão integrados no `tailwind.config.js`:

```tsx
// Cores BTS
<div className="bg-bts-blue text-white">
  <h1 className="text-bts-blue-highlight">Título</h1>
</div>

// Feedback
<button className="bg-bts-success">Sucesso</button>
<div className="text-bts-error">Erro</div>

// Neutros
<div className="bg-bts-gray-light border-bts-gray-base">
  <p className="text-bts-gray-dark">Texto</p>
</div>
```

### Usar CSS Variables

As cores também estão disponíveis como CSS variables em `index.css`:

```css
.my-component {
  background-color: var(--bts-blue);
  color: var(--bts-white);
  font-family: var(--font-family-primary);
}
```

## 🎯 Princípios Visuais BTS

1. **Sofisticado** - Paleta sóbria com azul escuro como cor principal
2. **Moderno** - Tipografia Montserrat clean e legível
3. **Confiável** - Hierarquia visual clara e consistente

## 📦 Mapeamento Shadcn UI

Os componentes shadcn/ui foram mapeados para usar as cores BTS:

| Shadcn Variable | Cor BTS | Hex |
|----------------|---------|-----|
| `--primary` | Blue Highlight | #1B5AB4 |
| `--secondary` | Blue Dark | #1B3857 |
| `--destructive` | Error | #E63939 |
| `--accent` | Blue 505 | #63C9F3 |
| `--muted` | Gray Light | #E4E4E4 |
| `--border` | Gray Base | #C6C6C6 |

## 🔄 Sincronização

Quando o BTS Design System for atualizado:

1. Atualizar os arquivos de tokens neste diretório
2. Atualizar `tailwind.config.js` se necessário
3. Atualizar CSS variables em `index.css` se necessário
4. Testar componentes para garantir consistência visual

## 📚 Referências

- [BTS Design System](https://github.com/BTS-Global/bts-design-system)
- [Princípios Visuais BTS](https://github.com/BTS-Global/bts-design-system/blob/main/docs/VISUAL_PRINCIPLES.md)
- [Figma Tokens](https://github.com/BTS-Global/bts-design-system/blob/main/docs/FIGMA_TOKENS.md)

## 🚀 Futuro

Quando o BTS Design System tiver componentes React ou Web Components, poderemos migrar para usar os componentes diretamente em vez de apenas os tokens.
