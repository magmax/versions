import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { Cluster } from './cluster';
import { Host } from './host';
import { ClusterService } from './cluster.service';
import { HostService } from './host.service';

@Component({
  selector: 'my-cluster-detail',
  templateUrl: 'app/cluster-detail.component.html',
  providers: [HostService]
})

export class ClusterDetailComponent implements OnInit, OnDestroy{
  sub: any;
  cluster: Cluster;
  hosts: Host[];

  constructor(
    private clusterService: ClusterService,
    private hostService: HostService,
    private route: ActivatedRoute,
    private router: Router
  ) {
  }

  ngOnInit() {
    this.sub = this.route.params.subscribe(params => {
      let id = +params['id'];
      this.clusterService.getCluster(id)
        .then(cluster => this.cluster = cluster);
      this.hostService.getHostsInCluster(id)
        .then(hosts => this.hosts = hosts);
    });
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }

  goBack() {
    window.history.back();
  }

  gotoHostDetail(host: Host) {
    let link = ['/host', host.id];
    this.router.navigate(link);
  }
}
