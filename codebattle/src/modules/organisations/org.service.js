/* ==========================================================================
   CODEBATTLE — MODULE: ORGANISATIONS SERVICE
   Location: src/modules/organisations/org.service.js
   ========================================================================== */

class OrgService {
  getOrganisations() {
    return [
      { id: "org1", name: "FAANG Interview Guild", members: 420, privateProblems: 18 },
      { id: "org2", name: "System Architects & OS Labs", members: 195, privateProblems: 12 }
    ];
  }
}

class OrganisationService extends OrgService {}

if (typeof window !== 'undefined') {
  window.OrgService = OrgService;
  window.OrganisationService = OrganisationService;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { OrgService, OrganisationService };
}
