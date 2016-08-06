import { Injectable } from '@angular/core';

import { Cluster } from './cluster';
import { CLUSTERS } from './mock-clusters';

@Injectable()
export class ClusterService {
  getClusters() {
    return Promise.resolve(CLUSTERS);
  }
  getCluster(id: number) {
    return this.getClusters()
             .then(clusters => clusters.find(cluster => cluster.id === id));
  }
}
