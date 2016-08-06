import { Injectable } from '@angular/core';

import { Host } from './host';
import { HOSTS } from './mock-hosts';

@Injectable()
export class HostService {
  getHosts() {
    return Promise.resolve(HOSTS);
  }
  getHost(id: number) {
    return this.getHosts()
             .then(clusters => clusters.find(cluster => cluster.id === id));
  }
  getHostsInCluster(id: number) {
    return this.getHosts()
             .then(hosts => hosts.filter(host => host.clusterId === id));

  }
}
