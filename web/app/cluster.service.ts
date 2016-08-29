import { Injectable } from '@angular/core';

import { Cluster } from './cluster';
import { CLUSTERS } from './mock-clusters';

@Injectable()
export class ClusterService {
  private url = "http://localhost:3001/cluster";

  constructor(private http: Http) { }

  getClusters() {
    // return Promise.resolve(CLUSTERS);

    return this.http.get(this.url)
      .toPromise()
      .then(response => response.json().data as Cluster[])
      .catch(this.handleError);
  }
  getCluster(id: number) {
    return this.getClusters()
             .then(clusters => clusters.find(cluster => cluster.id === id));
  }

  private handleError(error: any) {
    console.error('An error occurred', error);
    return Promise.reject(error.message || error);
  }
}
