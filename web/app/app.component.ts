import { Component }       from '@angular/core';
import { ROUTER_DIRECTIVES } from '@angular/router';

import { ClusterService }     from './cluster.service';
import { ClustersComponent } from './clusters.component';

@Component({
  selector: 'my-app',
  template: `
    <h1>{{title}}</h1>
    <my-clusters></my-clusters>
    <router-outlet></router-outlet>
  `,
  directives: [ROUTER_DIRECTIVES],
  providers: [
    ClusterService
  ]
})

export class AppComponent {
  title = 'ProjectBoard';
}
