import { OnInit, Component } from '@angular/core';
import { Router } from '@angular/router';

import { Cluster } from './cluster';

import { ClusterService } from './cluster.service';

@Component({
  selector: 'my-clusters',
  templateUrl: 'app/clusters.component.html',
  styleUrls: ['styles.css', 'app/clusters.component.css'],
  providers: []
})

export class ClustersComponent implements OnInit {
  selectedCluster: Cluster;
  clusters: Cluster[];

  constructor(
    private router: Router,
    private clusterService: ClusterService
  ) { }

  gotoDetail(cluster: Cluster) {
    let link = ['/cluster', cluster.id];
    this.router.navigate(link);
  }

  ngOnInit() {
    this.getClusters();
  }

  getClusters() {
    this.clusterService.getClusters().then(clusters => this.clusters = clusters);
  }
}
