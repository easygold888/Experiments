export const products = [
  {
    slug: 'vip-news-channel',
    name: 'VIP News Channel',
    tier: 'Core',
    priceUsd: 79,
    priceEth: 0.028,
    bestFor: 'Trader discrecional que necesita contexto macro + alertas ejecutables.',
    includes: [
      'Alertas macro/evento en tiempo real (XAUUSD-centric)',
      'Notas de ejecución: bias, invalidación y nivel operativo',
      'Brief diario pre-London y pre-NY',
      'Acceso Discord VIP + soporte de onboarding'
    ],
    excludes: ['No incluye gestión de cuenta', 'No garantiza rendimiento', 'No incluye asesoría financiera personalizada'],
    delivery: 'Acceso digital inmediato tras confirmaciones on-chain.',
    compatibility: ['TradingView', 'MT5', 'Bybit', 'Binance Futures'],
    riskNote: 'Producto educativo-operativo. Decisiones finales siempre del usuario.'
  },
  {
    slug: 'signal-engine-pro',
    name: 'Signal Engine Pro',
    tier: 'Pro',
    priceUsd: 149,
    priceEth: 0.052,
    bestFor: 'Operador con rutina diaria que quiere proceso sistemático y menos ruido.',
    includes: [
      'Todo lo de VIP News Channel',
      'Playbook de setups por régimen de volatilidad',
      'Checklist de validación pre-trade',
      'Weekly review con mapa de errores frecuentes'
    ],
    excludes: ['No ejecución automática de órdenes', 'No account management'],
    delivery: 'Acceso + playbook PDF/Notion en menos de 60 minutos después de confirmar.',
    compatibility: ['TradingView', 'MT5', 'Notion'],
    riskNote: 'No reemplaza gestión de riesgo ni disciplina de tamaño de posición.'
  },
  {
    slug: 'automation-blueprint',
    name: 'Automation Blueprint',
    tier: 'Elite',
    priceUsd: 299,
    priceEth: 0.106,
    bestFor: 'Equipo o trader técnico que quiere estandarizar pipeline y ejecución híbrida.',
    includes: [
      'Arquitectura de flujo signal → filtro → alerta → ejecución',
      'Plantillas de alerting y estados operativos',
      'Guía de instrumentación y tracking de performance',
      'Sesión de implementación (grabada)'
    ],
    excludes: ['No bot turnkey product', 'No custodia de fondos'],
    delivery: 'Entrega modular + sesión agendada tras confirmación.',
    compatibility: ['Webhooks', 'TradingView alerts', 'Discord bots', 'Google Sheets/DB'],
    riskNote: 'Implementación técnica requiere conocimientos operativos básicos.'
  }
];

export function findProduct(slug) {
  return products.find((p) => p.slug === slug);
}
