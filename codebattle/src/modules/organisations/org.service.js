/* ==========================================================================
   CODEBATTLE — MODULE: ORGANISATIONS SERVICE
   Location: src/modules/organisations/org.service.js
   ========================================================================== */

class OrganisationService {
  getOrganisations() {
    return [
      { id: "org1", name: "FAANG Interview Guild", members: 420, privateProblems: 18 },
      { id: "org2", name: "System Architects & OS Labs", members: 195, privateProblems: 12 }
    ];
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = OrganisationService;
}
