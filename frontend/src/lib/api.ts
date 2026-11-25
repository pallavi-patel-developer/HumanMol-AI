/**
 * HumanMol AI - Unified Scientific Engine API Client
 * Provides strictly typed asynchronous access to the FastAPI Scientific Engine.
 */

import {
  HealthResponse,
  MolecularDescriptorResponse,
  GenerationResponse,
  PropertyPredictionResponse,
  DockingResponse,
  DockingExperimentItem,
  ADMETResponse,
  TargetSearchResponse,
  EvidenceSearchResponse,
  XPertStatusResponse,
  PipelineRunResponse,
  BioactivityBenchmarkResponse,
  CompoundBioactivityResponse,
  SelectivityCheckRequest,
  SelectivityCheckResponse,
  CandidateBioactivityStatusResponse,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

class ApiClientError extends Error {
  status?: number;
  data?: any;

  constructor(message: string, status?: number, data?: any) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.data = data;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });

    if (!response.ok) {
      let errorData: any = null;
      try {
        errorData = await response.json();
      } catch {
        errorData = await response.text();
      }
      throw new ApiClientError(
        errorData?.detail || errorData?.message || `HTTP ${response.status} ${response.statusText}`,
        response.status,
        errorData
      );
    }

    return (await response.json()) as T;
  } catch (error: any) {
    if (error instanceof ApiClientError) {
      throw error;
    }
    throw new ApiClientError(
      `Failed to connect to Scientific Engine at ${API_BASE_URL}: ${error.message}`,
      0,
      error
    );
  }
}

export const scientificApi = {
  // 0. System Health & Status
  async getHealth(): Promise<HealthResponse> {
    return request<HealthResponse>('/health');
  },

  // 1. Core Chemistry (RDKit)
  async validateChemistry(smiles: string): Promise<MolecularDescriptorResponse> {
    return request<MolecularDescriptorResponse>('/api/chemistry/validate', {
      method: 'POST',
      body: JSON.stringify({ smiles }),
    });
  },

  // 2. Molecule Generation (REINVENT4)
  async generateMolecules(num_molecules: number = 10, seed?: number): Promise<GenerationResponse> {
    return request<GenerationResponse>('/api/generator/generate', {
      method: 'POST',
      body: JSON.stringify({ num_molecules, seed, batch_size: 32 }),
    });
  },

  // 3. Property Prediction (Chemprop D-MPNN)
  async predictProperties(smiles: string[]): Promise<PropertyPredictionResponse> {
    return request<PropertyPredictionResponse>('/api/properties/predict', {
      method: 'POST',
      body: JSON.stringify({ smiles }),
    });
  },

  // 4. Molecular Docking (AutoDock Vina)
  async runDocking(params: {
    ligand_smiles?: string;
    ligand_pdbqt_path?: string;
    target_pdb_id?: string;
    center_x?: number;
    center_y?: number;
    center_z?: number;
    size_x?: number;
    size_y?: number;
    size_z?: number;
    exhaustiveness?: number;
  }): Promise<DockingResponse> {
    return request<DockingResponse>('/api/docking/run', {
      method: 'POST',
      body: JSON.stringify({
        target_pdb_id: params.target_pdb_id || '2ITZ',
        ligand_smiles: params.ligand_smiles,
        ligand_pdbqt_path: params.ligand_pdbqt_path,
        center_x: params.center_x,
        center_y: params.center_y,
        center_z: params.center_z,
        size_x: params.size_x ?? 20.0,
        size_y: params.size_y ?? 20.0,
        size_z: params.size_z ?? 20.0,
        exhaustiveness: params.exhaustiveness ?? 8,
      }),
    });
  },

  async getDockingExperiments(limit: number = 20): Promise<DockingExperimentItem[]> {
    return request<DockingExperimentItem[]>(`/api/docking/experiments?limit=${limit}`);
  },

  async getDockingExperiment(experimentId: string): Promise<any> {
    return request<any>(`/api/docking/experiments/${encodeURIComponent(experimentId)}`);
  },

  async get2ItzRedockBenchmark(): Promise<any> {
    return request<any>('/api/docking/benchmark/2itz-redock');
  },

  async get2ITZBenchmarkAnalysis(): Promise<any> {
    return request<any>('/api/docking/benchmark/2itz-redock/analysis');
  },

  async get2ITZBenchmarkPoses(): Promise<{ target_pdb_id: string; is_benchmark: boolean; pdbqt_content: string }> {
    return request<{ target_pdb_id: string; is_benchmark: boolean; pdbqt_content: string }>('/api/docking/benchmark/2itz-redock/poses');
  },

  async getDockingExperimentPoses(experimentId: string): Promise<{ experiment_id: string; pdbqt_content: string }> {
    return request<{ experiment_id: string; pdbqt_content: string }>(`/api/docking/experiments/${encodeURIComponent(experimentId)}/poses`);
  },

  async getDockingExperimentReceptor(experimentId: string): Promise<{ experiment_id: string; target_pdb_id: string; format: string; content: string; sha256?: string }> {
    return request<{ experiment_id: string; target_pdb_id: string; format: string; content: string; sha256?: string }>(`/api/docking/experiments/${encodeURIComponent(experimentId)}/receptor`);
  },

  // 5. ADMET & Toxicity (ADMETlab 3.0)
  async predictADMET(smiles: string): Promise<ADMETResponse> {
    return request<ADMETResponse>('/api/admet/predict', {
      method: 'POST',
      body: JSON.stringify({ smiles }),
    });
  },

  // 6. Biological Target Intelligence (UniProt, ChEMBL, Reactome, AlphaFold, RCSB)
  async searchTargets(query: string, mutation: string = 'L858R', domain: string = 'kinase'): Promise<TargetSearchResponse> {
    return request<TargetSearchResponse>('/api/targets/search', {
      method: 'POST',
      body: JSON.stringify({
        query,
        mutation,
        domain,
        include_pathways: true,
        include_bioactivity: true,
        include_structures: true,
      }),
    });
  },

  async get2ITZRedockBenchmark(): Promise<any> {
    return request<any>('/api/docking/benchmark/2itz-redock');
  },

  // 7. Research Evidence (PubMed & arXiv)
  async searchEvidence(query: string, max_pubmed: number = 5, max_arxiv: number = 5): Promise<EvidenceSearchResponse> {
    return request<EvidenceSearchResponse>('/api/evidence/search', {
      method: 'POST',
      body: JSON.stringify({
        query,
        max_pubmed,
        max_arxiv,
      }),
    });
  },

  // 8. Human Cellular Response (XPert)
  async getXpertStatus(): Promise<XPertStatusResponse> {
    return request<XPertStatusResponse>('/api/xpert/status');
  },

  // 9. End-to-End Candidate Evaluation Pipeline
  async runPipeline(params: {
    target_name: string;
    num_candidates: number;
    seed?: number;
    run_properties?: boolean;
    run_docking?: boolean;
    run_admet?: boolean;
    target_protein?: string;
    disease?: string;
    mutation?: string;
    target_pdb_id?: string;
  }): Promise<PipelineRunResponse> {
    return request<PipelineRunResponse>('/api/pipeline/run', {
      method: 'POST',
      body: JSON.stringify({
        target_name: params.target_name,
        target_protein: params.target_protein || params.target_name,
        num_candidates: params.num_candidates,
        seed: params.seed ?? 42,
        run_properties: params.run_properties ?? true,
        run_docking: params.run_docking ?? true,
        run_admet: params.run_admet ?? true,
        disease: params.disease ?? 'NSCLC',
        mutation: params.mutation ?? (params.target_name.includes('EGFR') ? 'L858R' : 'Wild-Type'),
        target_pdb_id: params.target_pdb_id ?? (params.target_name.includes('EGFR') ? '2ITZ' : '1IEP'),
      }),
    });
  },

  async getPipelineRun(runId: string): Promise<PipelineRunResponse> {
    return request<PipelineRunResponse>(`/api/pipeline/runs/${runId}`);
  },

  // 10. Experimental Bioactivity & Selectivity Intelligence
  async getBioactivityBenchmark(): Promise<BioactivityBenchmarkResponse> {
    return request<BioactivityBenchmarkResponse>('/api/bioactivity/egfr-benchmark');
  },

  async getCompoundBioactivities(compoundId: string): Promise<CompoundBioactivityResponse> {
    return request<CompoundBioactivityResponse>(`/api/bioactivity/compound/${encodeURIComponent(compoundId)}`);
  },

  async checkSelectivity(params: SelectivityCheckRequest): Promise<SelectivityCheckResponse> {
    return request<SelectivityCheckResponse>('/api/bioactivity/selectivity-check', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  },

  async getCandidateBioactivityStatus(candidateId: string): Promise<CandidateBioactivityStatusResponse> {
    return request<CandidateBioactivityStatusResponse>(`/api/bioactivity/candidate/${encodeURIComponent(candidateId)}`);
  },
};
