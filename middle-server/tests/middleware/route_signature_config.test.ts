import { signatureValidationRoutes } from '../../src/middleware/route_signature_config';

describe('Signature Validation Route Configuration', () => {
  it('should have routes configured for signature validation', () => {
    // Validate that some critical routes are included
    const criticalRoutes = [
      '/builder/fetch-to-do',
      '/planner/add-pr-to-planner-todo',
      '/summarizer/trigger-fetch-audit-result',
      '/supporter/check-request'
    ];

    criticalRoutes.forEach(route => {
      expect(signatureValidationRoutes).toContain(route);
    });

    // Ensure the list is not empty
    expect(signatureValidationRoutes.length).toBeGreaterThan(0);
  });

  it('should have unique route entries', () => {
    const uniqueRoutes = new Set(signatureValidationRoutes);
    expect(uniqueRoutes.size).toBe(signatureValidationRoutes.length);
  });
});