import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Host } from './host';
import { HostService } from './host.service';

@Component({
  selector: 'my-host-detail',
  templateUrl: 'app/host-detail.component.html',
  providers: [HostService]
})

export class HostDetailComponent implements OnInit, OnDestroy{
  sub: any;
  host: Host;

  constructor(
    private hostService: HostService,
    private route: ActivatedRoute
  ) {
  }

  ngOnInit() {
    this.sub = this.route.params.subscribe(params => {
      let id = +params['id'];
      this.hostService.getHost(id)
        .then(host => this.host = host);
    });
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }

  goBack() {
    window.history.back();
  }
}
