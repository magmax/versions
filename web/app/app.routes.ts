import { provideRouter, RouterConfig }  from '@angular/router';
import { ClustersComponent } from './clusters.component';
import { ClusterDetailComponent } from './cluster-detail.component';
import { HostDetailComponent } from './host-detail.component';

const routes: RouterConfig = [
  {
    path: 'clusters',
    component: ClustersComponent
  },
  {
    path: '#/clusters',
    component: ClustersComponent
  },
  {
    path: '',
    redirectTo: '/#/clusters',
    pathMatch: 'full'
  },
  {
    path: 'cluster/:id',
    component: ClusterDetailComponent
  },
  {
    path: 'host/:id',
    component: HostDetailComponent
  },
];

export const appRouterProviders = [
  provideRouter(routes)
];
