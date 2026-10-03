# Holdout v5 Hand-Labelling Worksheet (blind re-label under D-38)

**Target corpus**: `tests/fixtures/holdout_v5/` (40 logs)
**Generated**: 2026-10-03 by `analysis/build_holdout_v5_worksheet.py`
**Governing decisions**: D-27, D-29, D-37, D-38
**Protocol**: `docs/phase/013B-holdout-v5-protocol.md` (APPROVED, seed `20261111`)
**Supersedes**: `docs/phase/024-holdout-v5-worksheet.md`, whose scoring was VOID
under D-38 because Expected Class was derived by rule rather than hand-labelled.
The corpus was therefore never consumed and is labelled again here.

## How to fill this in

Every field below is blank and must stay blank until a human fills it. No
BlastRadius code, grep or regex produced any value in this file, and none may be
used to fill it (D-38).

1. Open the fixture named in the section. **The full fixture is authoritative.**
   The excerpt is the final 120 lines only, chosen without looking at the
   content, so a failure earlier in the log will not appear in it.
2. Fill **Build Tool** yourself from the log. It is deliberately not given.
3. Fill **Expected Class** as an independent judgement, one of
   `TEST_FAILURE`, `NO_TEST_OUTPUT`, `TEST_RAN_CLEAN`. Do **not** derive it from
   how many identifiers you listed -- deriving it is what voided the last run.
4. Fill **Expected Identifier Count** and **Expected Identifiers**. Write
   `NO_TEST_OUTCOMES` for the identifier list when there are none.
5. Fill **Confidence** as `CERTAIN` or `UNCERTAIN`.

`analysis/score_holdout_v5.py` refuses to run while any cell is empty, and
refuses to run a second time. Scoring is a single irreversible event (D-37).

## Isolation

Zero job-id overlap with the development fixtures, holdout v1/v2, v3, v4, or with
any log examined during the 2026-10-03 parameter-type characterisation
(`docs/session/holdout-exclusion.txt` and the 13 jobs listed in the step-2
supersession table). Verified before generation.

---

## 1. `Stirling-Tools__Stirling-PDF__089792061823.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/Stirling-Tools__Stirling-PDF__089792061823.txt` (authoritative; read this, not the excerpt)
- **Repository**: `Stirling-Tools/Stirling-PDF`
- **Content hash (sha256, first 16)**: `47a1c37d5b33ee63`
- **Body size**: 539,615 bytes, 1,446 lines
- **Excerpt**: final 120 of 1,446 lines, content-blind

```text
2026-07-26T12:12:07.9526418Z Sun, 26 Jul 2026 12:09:47 GMT:domain resolved: repo.maven.apache.org., ip address: 104.18.18.12, TTL: 300
2026-07-26T12:12:07.9527320Z Sun, 26 Jul 2026 12:09:47 GMT:endpoint called ip address:port 104.18.18.12:443, domain: repo.maven.apache.org., pid: 3567, process: java
2026-07-26T12:12:07.9528200Z Sun, 26 Jul 2026 12:10:06 GMT:domain resolved: repository.jboss.org., ip address: 23.67.33.24, TTL: 30
2026-07-26T12:12:07.9529065Z Sun, 26 Jul 2026 12:10:06 GMT:endpoint called ip address:port 23.67.33.24:443, domain: repository.jboss.org., pid: 3567, process: java
2026-07-26T12:12:07.9530052Z Sun, 26 Jul 2026 12:10:48 GMT:domain resolved: repository.jboss.org., ip address: 23.67.33.20, TTL: 30
2026-07-26T12:12:07.9531049Z Sun, 26 Jul 2026 12:10:48 GMT:endpoint called ip address:port 23.67.33.20:443, domain: repository.jboss.org., pid: 3567, process: java
2026-07-26T12:12:07.9531999Z Sun, 26 Jul 2026 12:11:52 GMT:domain resolved: prod.app-api.stepsecurity.io., ip address: 32.184.56.213, TTL: 30
2026-07-26T12:12:07.9533000Z Sun, 26 Jul 2026 12:11:52 GMT:endpoint called ip address:port 168.63.129.16:53, domain: , pid: 2278, process: systemd-resolved
2026-07-26T12:12:07.9534167Z Sun, 26 Jul 2026 12:11:55 GMT:endpoint called ip address:port 8.8.8.8:53, domain: , pid: 3945, process: java
2026-07-26T12:12:07.9535616Z Sun, 26 Jul 2026 12:12:04 GMT:domain resolved: results-receiver.actions.githubusercontent.com., ip address: 140.82.112.22, TTL: 31
2026-07-26T12:12:07.9536837Z Sun, 26 Jul 2026 12:12:04 GMT:endpoint called ip address:port 140.82.112.22:443, domain: results-receiver.actions.githubusercontent.com., pid: 5701, process: node
2026-07-26T12:12:07.9538010Z Sun, 26 Jul 2026 12:12:04 GMT:domain resolved: productionresultssa18.blob.core.windows.net., ip address: 20.150.88.228, TTL: 30
2026-07-26T12:12:07.9539488Z Sun, 26 Jul 2026 12:12:04 GMT:endpoint called ip address:port 20.150.88.228:443, domain: productionresultssa18.blob.core.windows.net., pid: 5701, process: node
2026-07-26T12:12:07.9540450Z 
2026-07-26T12:12:07.9540686Z Sun, 26 Jul 2026 12:12:06 GMT:post_event called
2026-07-26T12:12:07.9540931Z 
2026-07-26T12:12:07.9541040Z status:
2026-07-26T12:12:07.9541294Z Initialized
2026-07-26T12:12:07.9630593Z agent.service log:
2026-07-26T12:12:07.9632255Z Jul 26 12:08:55 runnervmvrwv9 systemd[1]: /etc/systemd/system/agent.service:9: Standard output type syslog is obsolete, automatically updating to journal. Please update your unit file, and consider removing the setting altogether.
2026-07-26T12:12:07.9635320Z Jul 26 12:08:55 runnervmvrwv9 systemd[1]: /etc/systemd/system/agent.service:10: Standard output type syslog is obsolete, automatically updating to journal. Please update your unit file, and consider removing the setting altogether.
2026-07-26T12:12:07.9637031Z Jul 26 12:08:55 runnervmvrwv9 systemd[1]: Started agent.service - Agent.
2026-07-26T12:12:07.9638519Z Jul 26 12:08:55 runnervmvrwv9 sudo[2270]:     root : *** ; USER=root ; COMMAND=/usr/bin/systemctl stop systemd-resolved
2026-07-26T12:12:07.9639817Z Jul 26 12:08:55 runnervmvrwv9 sudo[2270]: pam_unix(sudo:session): session opened for user root(uid=0) by (uid=0)
2026-07-26T12:12:07.9641020Z Jul 26 12:08:55 runnervmvrwv9 sudo[2270]: pam_unix(sudo:session): session closed for user root
2026-07-26T12:12:07.9642415Z Jul 26 12:08:55 runnervmvrwv9 sudo[2276]:     root : *** ; USER=root ; COMMAND=/usr/bin/systemctl restart systemd-resolved
2026-07-26T12:12:07.9644044Z Jul 26 12:08:55 runnervmvrwv9 sudo[2276]: pam_unix(sudo:session): session opened for user root(uid=0) by (uid=0)
2026-07-26T12:12:07.9645318Z Jul 26 12:08:55 runnervmvrwv9 sudo[2276]: pam_unix(sudo:session): session closed for user root
2026-07-26T12:12:07.9646785Z Jul 26 12:08:55 runnervmvrwv9 sudo[2282]:     root : *** ; USER=root ; COMMAND=/usr/bin/resolvectl flush-caches
2026-07-26T12:12:07.9648056Z Jul 26 12:08:55 runnervmvrwv9 sudo[2282]: pam_unix(sudo:session): session opened for user root(uid=0) by (uid=0)
2026-07-26T12:12:07.9649259Z Jul 26 12:08:55 runnervmvrwv9 sudo[2282]: pam_unix(sudo:session): session closed for user root
2026-07-26T12:12:07.9650664Z Jul 26 12:08:55 runnervmvrwv9 sudo[2285]:     root : *** ; USER=root ; COMMAND=/usr/bin/systemctl reload docker
2026-07-26T12:12:07.9652007Z Jul 26 12:08:55 runnervmvrwv9 sudo[2285]: pam_unix(sudo:session): session opened for user root(uid=0) by (uid=0)
2026-07-26T12:12:07.9653352Z Jul 26 12:08:55 runnervmvrwv9 sudo[2285]: pam_unix(sudo:session): session closed for user root
2026-07-26T12:12:07.9654669Z Jul 26 12:08:55 runnervmvrwv9 sudo[2293]:     root : *** ; USER=root ; COMMAND=/usr/bin/systemctl daemon-reload
2026-07-26T12:12:07.9656257Z Jul 26 12:08:55 runnervmvrwv9 sudo[2293]: pam_unix(sudo:session): session opened for user root(uid=0) by (uid=0)
2026-07-26T12:12:07.9658558Z Jul 26 12:08:55 runnervmvrwv9 systemd[1]: /etc/systemd/system/agent.service:9: Standard output type syslog is obsolete, automatically updating to journal. Please update your unit file, and consider removing the setting altogether.
2026-07-26T12:12:07.9661469Z Jul 26 12:08:55 runnervmvrwv9 systemd[1]: /etc/systemd/system/agent.service:10: Standard output type syslog is obsolete, automatically updating to journal. Please update your unit file, and consider removing the setting altogether.
2026-07-26T12:12:07.9663652Z Jul 26 12:08:55 runnervmvrwv9 sudo[2293]: pam_unix(sudo:session): session closed for user root
2026-07-26T12:12:07.9665075Z Jul 26 12:08:55 runnervmvrwv9 sudo[2364]:     root : *** ; USER=root ; COMMAND=/usr/bin/systemctl restart docker
2026-07-26T12:12:07.9666359Z Jul 26 12:08:55 runnervmvrwv9 sudo[2364]: pam_unix(sudo:session): session opened for user root(uid=0) by (uid=0)
2026-07-26T12:12:07.9667559Z Jul 26 12:08:58 runnervmvrwv9 sudo[2364]: pam_unix(sudo:session): session closed for user root
2026-07-26T12:12:07.9669290Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Fetching custom detection rules module=armour api_url=https://agent.api.stepsecurity.io/v1 repo=Stirling-Tools/Stirling-PDF
2026-07-26T12:12:07.9670844Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: [armour-cdr] Event Policy:  package hardenrunner.event
2026-07-26T12:12:07.9671861Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: import rego.v1
2026-07-26T12:12:07.9673185Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: # Rule: Agent - Event System Rule (707af3d3-11d5-4cce-abab-8e6dfcfc510c)
2026-07-26T12:12:07.9674317Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: default runner_worker_mem_read := false
2026-07-26T12:12:07.9675097Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 
2026-07-26T12:12:07.9675805Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: runner_worker_mem_read if {
2026-07-26T12:12:07.9676649Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     evt := input.armour_event
2026-07-26T12:12:07.9677463Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     evt.kind == "FILE_READ"
2026-07-26T12:12:07.9678261Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     evt.file_info != null
2026-07-26T12:12:07.9679200Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     endswith(evt.file_info.current_exe, "python")
2026-07-26T12:12:07.9680250Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     startswith(evt.file_info.target_file, "/proc")
2026-07-26T12:12:07.9681303Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     endswith(evt.file_info.target_file, "/mem")
2026-07-26T12:12:07.9682424Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     endswith(evt.file_info.target_exe, "Runner.Worker")
2026-07-26T12:12:07.9683480Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: }
2026-07-26T12:12:07.9684024Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 
2026-07-26T12:12:07.9684716Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: runner_worker_mem_read if {
2026-07-26T12:12:07.9685548Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     evt := input.armour_event
2026-07-26T12:12:07.9686370Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     evt.kind == "FILE_READ"
2026-07-26T12:12:07.9687194Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     evt.file_info != null
2026-07-26T12:12:07.9688096Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     endswith(evt.file_info.current_exe, "python3")
2026-07-26T12:12:07.9689146Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     startswith(evt.file_info.target_file, "/proc")
2026-07-26T12:12:07.9690215Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     endswith(evt.file_info.target_file, "/mem")
2026-07-26T12:12:07.9691243Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     endswith(evt.file_info.target_exe, "Runner.Worker")
2026-07-26T12:12:07.9692085Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: }
2026-07-26T12:12:07.9693347Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 
2026-07-26T12:12:07.9694197Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: default suspicious_file_access := false
2026-07-26T12:12:07.9695288Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: suspicious_file_access := true if {
2026-07-26T12:12:07.9696406Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     contains(input.file_event.file_name, "router_init.js")
2026-07-26T12:12:07.9697935Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     input.file_event.checksum == "ab4fcadaec49c03278063dd269ea5eef82d24f2124a8e15d7b90f2fa8601266c"
2026-07-26T12:12:07.9699156Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: }
2026-07-26T12:12:07.9700059Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: [armour-cdr] State Policy:  package hardenrunner.state
2026-07-26T12:12:07.9701040Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: import rego.v1
2026-07-26T12:12:07.9702110Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: # Rule: Agent - State System Rule (a6dabdfb-ba5b-4932-bf3c-ed621582dbce)
2026-07-26T12:12:07.9704118Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: default action := ""
2026-07-26T12:12:07.9704818Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 
2026-07-26T12:12:07.9705523Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: lockdown_required if {
2026-07-26T12:12:07.9706438Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     input.state.runner_worker_mem_read
2026-07-26T12:12:07.9707312Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: }
2026-07-26T12:12:07.9707922Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 
2026-07-26T12:12:07.9708624Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: lockdown_required if {
2026-07-26T12:12:07.9709484Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     input.state.suspicious_file_access
2026-07-26T12:12:07.9710230Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: }
2026-07-26T12:12:07.9710766Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 
2026-07-26T12:12:07.9711445Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: action := "lockdown" if {
2026-07-26T12:12:07.9712251Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]:     lockdown_required
2026-07-26T12:12:07.9713070Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: }
2026-07-26T12:12:07.9713923Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: [armour-cdr] Checksum Paths:  [router_init.js]
2026-07-26T12:12:07.9715179Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Custom detection rules evaluator initialized module=armour
2026-07-26T12:12:07.9716729Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Detection manager started module=detection-manager workers=4 buffer_size=1000
2026-07-26T12:12:07.9718151Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Config module=armour ENFORCE_READ_BLOCK=false
2026-07-26T12:12:07.9719533Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Config module=armour ENFORCE_WRITE_BLOCK=false
2026-07-26T12:12:07.9720868Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Config module=armour ENFORCE_KILL_BLOCK=false
2026-07-26T12:12:07.9722181Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Config module=armour AGENT_PID=2257
2026-07-26T12:12:07.9723177Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Map size module=armour protected_pids=1
2026-07-26T12:12:07.9723924Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Map size module=armour protected_pid_inodes=1
2026-07-26T12:12:07.9724649Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Map size module=armour protected_bpf_ids=9
2026-07-26T12:12:07.9725373Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Map size module=armour protected_fs_inodes=6
2026-07-26T12:12:07.9726306Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Map size module=armour protected_proc_fs_inodes=2
2026-07-26T12:12:07.9727161Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Map size module=armour events=16384
2026-07-26T12:12:07.9727900Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO ProtectedPids module=armour pids=map[2258:2257]
2026-07-26T12:12:07.9728670Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO ProtectedBPFIDs module=armour ids="[18 12 16 19 17]"
2026-07-26T12:12:07.9729519Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO File Info module=armour inoKey="{Device:24 Inode:16938}" path=/proc/2122/mem
2026-07-26T12:12:07.9730457Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO File Info module=armour inoKey="{Device:24 Inode:16939}" path=/proc/2071/mem
2026-07-26T12:12:07.9731441Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO File Info module=armour inoKey="{Device:2049 Inode:89486}" path=/etc/sudoers.d/runner
2026-07-26T12:12:07.9732434Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO File Info module=armour inoKey="{Device:28 Inode:911}" path=/etc/resolv.conf
2026-07-26T12:12:07.9734128Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO File Info module=armour inoKey="{Device:2049 Inode:508}" path=/etc/systemd/resolved.conf
2026-07-26T12:12:07.9735699Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO File Info module=armour inoKey="{Device:2049 Inode:291419}" path=/etc/docker/daemon.json
2026-07-26T12:12:07.9736568Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Protection maps populated module=armour
2026-07-26T12:12:07.9737299Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Protection maps are freezed module=armour
2026-07-26T12:12:07.9737992Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Linking completed module=armour
2026-07-26T12:12:07.9738659Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Armour engaged module=armour
2026-07-26T12:12:07.9739350Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO RingBuffer created module=armour size=16384
2026-07-26T12:12:07.9740048Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO Listening for events module=armour
2026-07-26T12:12:07.9740793Z Jul 26 12:08:58 runnervmvrwv9 agentservice[2257]: 2026/07/26 12:08:58 INFO [LOCKDOWN] Runner.Worker PID set module=armour pid=2122
2026-07-26T12:12:07.9741253Z 
2026-07-26T12:12:07.9799054Z Cleaning up orphan processes
2026-07-26T12:12:08.0217164Z Terminate orphan process: pid (3567) (java)
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 2. `Stirling-Tools__Stirling-PDF__092039331010.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/Stirling-Tools__Stirling-PDF__092039331010.txt` (authoritative; read this, not the excerpt)
- **Repository**: `Stirling-Tools/Stirling-PDF`
- **Content hash (sha256, first 16)**: `e52a595a5742b8ad`
- **Body size**: 236,808 bytes, 2,002 lines
- **Excerpt**: final 120 of 2,002 lines, content-blind

```text
2026-08-04T15:25:57.7453260Z Tue, 04 Aug 2026 15:20:50 GMT:domain resolved: dl.min.io., ip address: 138.68.11.125, TTL: 30
2026-08-04T15:25:57.7453801Z Tue, 04 Aug 2026 15:20:50 GMT:domain resolved: github.com., ip address: 140.82.114.4, TTL: 38
2026-08-04T15:25:57.7454571Z Tue, 04 Aug 2026 15:20:50 GMT:endpoint called ip address:port 140.82.114.4:443, domain: github.com., pid: 3891, process: minio
2026-08-04T15:25:57.7455450Z Tue, 04 Aug 2026 15:20:50 GMT:endpoint called ip address:port 185.199.111.133:443, domain: release-assets.githubusercontent.com., pid: 3891, process: minio
2026-08-04T15:25:57.7456539Z Tue, 04 Aug 2026 15:20:50 GMT:endpoint called ip address:port 138.68.11.125:443, domain: dl.min.io., pid: 3891, process: minio
2026-08-04T15:25:57.7457461Z Tue, 04 Aug 2026 15:21:04 GMT:endpoint called ip address:port 168.63.129.16:80, domain: , pid: 3979, process: python3.12
2026-08-04T15:25:57.7458522Z Tue, 04 Aug 2026 15:21:15 GMT:endpoint called ip address:port 8.8.8.8:53, domain: , pid: 3454, process: java
2026-08-04T15:25:57.7459269Z Tue, 04 Aug 2026 15:21:29 GMT:domain resolved: registry-1.docker.io., ip address: 54.174.143.237, TTL: 30
2026-08-04T15:25:57.7460835Z Tue, 04 Aug 2026 15:21:29 GMT:endpoint called ip address:port 54.174.143.237:443, domain: registry-1.docker.io., pid: 2470, process: dockerd
2026-08-04T15:25:57.7461737Z Tue, 04 Aug 2026 15:21:32 GMT:domain resolved: localstack.cloud., ip address: 198.202.211.1, TTL: 1974
2026-08-04T15:25:57.7462363Z Tue, 04 Aug 2026 15:21:32 GMT:domain resolved: assets.localstack.cloud., ip address: 3.170.185.35, TTL: 60
2026-08-04T15:25:57.7463236Z Tue, 04 Aug 2026 15:21:32 GMT:domain resolved: analytics.localstack.cloud., ip address: 63.185.236.196, TTL: 40
2026-08-04T15:25:57.7464499Z Tue, 04 Aug 2026 15:21:32 GMT:endpoint called ip address:port 3.170.185.35:443, domain: assets.localstack.cloud., pid: 4462, process: python3.11
2026-08-04T15:25:57.7467540Z Tue, 04 Aug 2026 15:21:32 GMT:endpoint called ip address:port 63.185.236.196:443, domain: analytics.localstack.cloud., pid: 4462, process: python3.11
2026-08-04T15:25:57.7468817Z Tue, 04 Aug 2026 15:22:03 GMT:domain resolved: registry-1.docker.io., ip address: 34.226.128.83, TTL: 45
2026-08-04T15:25:57.7470210Z Tue, 04 Aug 2026 15:22:03 GMT:endpoint called ip address:port 34.226.128.83:443, domain: registry-1.docker.io., pid: 2470, process: dockerd
2026-08-04T15:25:57.7471404Z Tue, 04 Aug 2026 15:22:04 GMT:domain resolved: production.cloudfront.docker.com., ip address: 13.227.87.62, TTL: 60
2026-08-04T15:25:57.7472739Z Tue, 04 Aug 2026 15:22:04 GMT:endpoint called ip address:port 13.227.87.62:443, domain: production.cloudfront.docker.com., pid: 2470, process: dockerd
2026-08-04T15:25:57.7473607Z Tue, 04 Aug 2026 15:22:14 GMT:unable to resolve domain: api.vendor.example. err: unable to resolve domain api.vendor.example., status 3
2026-08-04T15:25:57.7474298Z Tue, 04 Aug 2026 15:22:26 GMT:domain resolved: dl.min.io., ip address: 138.68.11.125, TTL: 360
2026-08-04T15:25:57.7475111Z Tue, 04 Aug 2026 15:22:26 GMT:endpoint called ip address:port 138.68.11.125:443, domain: dl.min.io., pid: 5790, process: minio
2026-08-04T15:25:57.7475780Z Tue, 04 Aug 2026 15:22:26 GMT:domain resolved: github.com., ip address: 140.82.113.3, TTL: 60
2026-08-04T15:25:57.7476420Z Tue, 04 Aug 2026 15:22:26 GMT:endpoint called ip address:port 140.82.113.3:443, domain: github.com., pid: 5790, process: minio
2026-08-04T15:25:57.7477243Z Tue, 04 Aug 2026 15:22:26 GMT:endpoint called ip address:port 185.199.111.133:443, domain: release-assets.githubusercontent.com., pid: 5790, process: minio
2026-08-04T15:25:57.7478264Z Tue, 04 Aug 2026 15:22:29 GMT:endpoint called ip address:port 138.68.11.125:443, domain: dl.min.io., pid: 5969, process: minio
2026-08-04T15:25:57.7478974Z Tue, 04 Aug 2026 15:22:29 GMT:endpoint called ip address:port 140.82.113.3:443, domain: github.com., pid: 5969, process: minio
2026-08-04T15:25:57.7480143Z Tue, 04 Aug 2026 15:22:29 GMT:endpoint called ip address:port 185.199.111.133:443, domain: release-assets.githubusercontent.com., pid: 5969, process: minio
2026-08-04T15:25:57.7481489Z Tue, 04 Aug 2026 15:22:54 GMT:endpoint called ip address:port 138.68.11.125:443, domain: dl.min.io., pid: 6155, process: minio
2026-08-04T15:25:57.7482685Z Tue, 04 Aug 2026 15:22:54 GMT:endpoint called ip address:port 140.82.113.3:443, domain: github.com., pid: 6155, process: minio
2026-08-04T15:25:57.7483652Z Tue, 04 Aug 2026 15:22:54 GMT:endpoint called ip address:port 185.199.111.133:443, domain: release-assets.githubusercontent.com., pid: 6155, process: minio
2026-08-04T15:25:57.7484569Z Tue, 04 Aug 2026 15:23:34 GMT:domain resolved: results-receiver.actions.githubusercontent.com., ip address: 140.82.112.22, TTL: 30
2026-08-04T15:25:57.7485521Z Tue, 04 Aug 2026 15:23:34 GMT:endpoint called ip address:port 140.82.112.22:443, domain: results-receiver.actions.githubusercontent.com., pid: 2225, process: Runner.Worker
2026-08-04T15:25:57.7486462Z Tue, 04 Aug 2026 15:23:35 GMT:domain resolved: productionresultssa6.blob.core.windows.net., ip address: 20.209.112.225, TTL: 30
2026-08-04T15:25:57.7487376Z Tue, 04 Aug 2026 15:23:35 GMT:endpoint called ip address:port 20.209.112.225:443, domain: productionresultssa6.blob.core.windows.net., pid: 2225, process: Runner.Worker
2026-08-04T15:25:57.7488494Z Tue, 04 Aug 2026 15:23:37 GMT:domain resolved: productionresultssa17.blob.core.windows.net., ip address: 52.239.172.36, TTL: 30
2026-08-04T15:25:57.7489405Z Tue, 04 Aug 2026 15:23:37 GMT:endpoint called ip address:port 140.82.112.22:443, domain: results-receiver.actions.githubusercontent.com., pid: 6340, process: node
2026-08-04T15:25:57.7490715Z Tue, 04 Aug 2026 15:23:37 GMT:endpoint called ip address:port 52.239.172.36:443, domain: productionresultssa17.blob.core.windows.net., pid: 6340, process: node
2026-08-04T15:25:57.7491553Z Tue, 04 Aug 2026 15:23:39 GMT:domain resolved: registry-1.docker.io., ip address: 3.210.130.203, TTL: 30
2026-08-04T15:25:57.7492276Z Tue, 04 Aug 2026 15:23:39 GMT:endpoint called ip address:port 3.210.130.203:443, domain: registry-1.docker.io., pid: 2470, process: dockerd
2026-08-04T15:25:57.7493046Z Tue, 04 Aug 2026 15:23:42 GMT:domain resolved: production.cloudfront.docker.com., ip address: 13.249.141.13, TTL: 60
2026-08-04T15:25:57.7493855Z Tue, 04 Aug 2026 15:23:42 GMT:endpoint called ip address:port 13.249.141.13:443, domain: production.cloudfront.docker.com., pid: 2470, process: dockerd
2026-08-04T15:25:57.7494701Z Tue, 04 Aug 2026 15:23:46 GMT:endpoint called ip address:port 104.18.43.178:443, domain: auth.docker.io., pid: 7365, process: docker-buildx
2026-08-04T15:25:57.7495633Z Tue, 04 Aug 2026 15:23:47 GMT:domain resolved: security.ubuntu.com., ip address: 91.189.92.23, TTL: 30
2026-08-04T15:25:57.7496236Z Tue, 04 Aug 2026 15:23:47 GMT:domain resolved: archive.ubuntu.com., ip address: 91.189.92.24, TTL: 30
2026-08-04T15:25:57.7496903Z Tue, 04 Aug 2026 15:23:47 GMT:endpoint called ip address:port 91.189.92.23:80, domain: security.ubuntu.com., pid: 7461, process: http
2026-08-04T15:25:57.7497651Z Tue, 04 Aug 2026 15:23:47 GMT:endpoint called ip address:port 91.189.92.24:80, domain: archive.ubuntu.com., pid: 7462, process: http
2026-08-04T15:25:57.7498452Z Tue, 04 Aug 2026 15:25:39 GMT:domain resolved: hosted-compute-watchdog-prod-iad-02.githubapp.com., ip address: 140.82.113.24, TTL: 30
2026-08-04T15:25:57.7499223Z Tue, 04 Aug 2026 15:25:39 GMT:domain resolved: prod.app-api.stepsecurity.io., ip address: 50.112.240.79, TTL: 30
2026-08-04T15:25:57.7499858Z Tue, 04 Aug 2026 15:25:46 GMT:domain resolved: archive.ubuntu.com., ip address: 91.189.91.81, TTL: 55
2026-08-04T15:25:57.7500732Z Tue, 04 Aug 2026 15:25:46 GMT:endpoint called ip address:port 91.189.91.81:80, domain: archive.ubuntu.com., pid: 7623, process: http
2026-08-04T15:25:57.7501539Z Tue, 04 Aug 2026 15:25:53 GMT:domain resolved: security.ubuntu.com., ip address: 91.189.91.81, TTL: 30
2026-08-04T15:25:57.7502208Z Tue, 04 Aug 2026 15:25:53 GMT:endpoint called ip address:port 91.189.91.81:80, domain: security.ubuntu.com., pid: 7649, process: http
2026-08-04T15:25:57.7503008Z Tue, 04 Aug 2026 15:25:54 GMT:domain resolved: results-receiver.actions.githubusercontent.com., ip address: 140.82.112.21, TTL: 41
2026-08-04T15:25:57.7503923Z Tue, 04 Aug 2026 15:25:54 GMT:endpoint called ip address:port 140.82.112.21:443, domain: results-receiver.actions.githubusercontent.com., pid: 7671, process: node
2026-08-04T15:25:57.7504838Z Tue, 04 Aug 2026 15:25:54 GMT:domain resolved: productionresultssa6.blob.core.windows.net., ip address: 20.209.113.193, TTL: 30
2026-08-04T15:25:57.7505793Z Tue, 04 Aug 2026 15:25:54 GMT:endpoint called ip address:port 140.82.112.21:443, domain: results-receiver.actions.githubusercontent.com., pid: 2225, process: Runner.Worker
2026-08-04T15:25:57.7506807Z Tue, 04 Aug 2026 15:25:54 GMT:endpoint called ip address:port 20.209.113.193:443, domain: productionresultssa6.blob.core.windows.net., pid: 7671, process: node
2026-08-04T15:25:57.7507809Z Tue, 04 Aug 2026 15:25:54 GMT:endpoint called ip address:port 20.209.113.193:443, domain: productionresultssa6.blob.core.windows.net., pid: 2225, process: Runner.Worker
2026-08-04T15:25:57.7508809Z Tue, 04 Aug 2026 15:25:55 GMT:endpoint called ip address:port 140.82.112.21:443, domain: results-receiver.actions.githubusercontent.com., pid: 7826, process: node
2026-08-04T15:25:57.7509351Z 
2026-08-04T15:25:57.7509641Z Tue, 04 Aug 2026 15:25:56 GMT:post_event called
2026-08-04T15:25:57.7509862Z 
2026-08-04T15:25:57.7510049Z status:
2026-08-04T15:25:57.7510260Z Initialized
2026-08-04T15:25:57.7544327Z agent.service log:
2026-08-04T15:25:57.7545748Z Aug 04 15:17:23 runnervmvrwv9 systemd[1]: /etc/systemd/system/agent.service:9: Standard output type syslog is obsolete, automatically updating to journal. Please update your unit file, and consider removing the setting altogether.
2026-08-04T15:25:57.7548160Z Aug 04 15:17:23 runnervmvrwv9 systemd[1]: /etc/systemd/system/agent.service:10: Standard output type syslog is obsolete, automatically updating to journal. Please update your unit file, and consider removing the setting altogether.
2026-08-04T15:25:57.7549391Z Aug 04 15:17:23 runnervmvrwv9 systemd[1]: Started agent.service - Agent.
2026-08-04T15:25:57.7550423Z Aug 04 15:17:23 runnervmvrwv9 sudo[2374]:     root : *** ; USER=root ; COMMAND=/usr/bin/systemctl stop systemd-resolved
2026-08-04T15:25:57.7551192Z Aug 04 15:17:23 runnervmvrwv9 sudo[2374]: pam_unix(sudo:session): session opened for user root(uid=0) by (uid=0)
2026-08-04T15:25:57.7551869Z Aug 04 15:17:23 runnervmvrwv9 sudo[2374]: pam_unix(sudo:session): session closed for user root
2026-08-04T15:25:57.7552999Z Aug 04 15:17:23 runnervmvrwv9 sudo[2380]:     root : *** ; USER=root ; COMMAND=/usr/bin/systemctl restart systemd-resolved
2026-08-04T15:25:57.7553760Z Aug 04 15:17:23 runnervmvrwv9 sudo[2380]: pam_unix(sudo:session): session opened for user root(uid=0) by (uid=0)
2026-08-04T15:25:57.7554472Z Aug 04 15:17:23 runnervmvrwv9 sudo[2380]: pam_unix(sudo:session): session closed for user root
2026-08-04T15:25:57.7555229Z Aug 04 15:17:23 runnervmvrwv9 sudo[2385]:     root : *** ; USER=root ; COMMAND=/usr/bin/resolvectl flush-caches
2026-08-04T15:25:57.7555959Z Aug 04 15:17:23 runnervmvrwv9 sudo[2385]: pam_unix(sudo:session): session opened for user root(uid=0) by (uid=0)
2026-08-04T15:25:57.7556626Z Aug 04 15:17:23 runnervmvrwv9 sudo[2385]: pam_unix(sudo:session): session closed for user root
2026-08-04T15:25:57.7557297Z Aug 04 15:17:23 runnervmvrwv9 sudo[2388]:     root : *** ; USER=root ; COMMAND=/usr/bin/systemctl reload docker
2026-08-04T15:25:57.7557982Z Aug 04 15:17:23 runnervmvrwv9 sudo[2388]: pam_unix(sudo:session): session opened for user root(uid=0) by (uid=0)
2026-08-04T15:25:57.7558736Z Aug 04 15:17:23 runnervmvrwv9 sudo[2388]: pam_unix(sudo:session): session closed for user root
2026-08-04T15:25:57.7559479Z Aug 04 15:17:23 runnervmvrwv9 sudo[2401]:     root : *** ; USER=root ; COMMAND=/usr/bin/systemctl daemon-reload
2026-08-04T15:25:57.7560326Z Aug 04 15:17:23 runnervmvrwv9 sudo[2401]: pam_unix(sudo:session): session opened for user root(uid=0) by (uid=0)
2026-08-04T15:25:57.7561539Z Aug 04 15:17:23 runnervmvrwv9 systemd[1]: /etc/systemd/system/agent.service:9: Standard output type syslog is obsolete, automatically updating to journal. Please update your unit file, and consider removing the setting altogether.
2026-08-04T15:25:57.7563318Z Aug 04 15:17:23 runnervmvrwv9 systemd[1]: /etc/systemd/system/agent.service:10: Standard output type syslog is obsolete, automatically updating to journal. Please update your unit file, and consider removing the setting altogether.
2026-08-04T15:25:57.7564390Z Aug 04 15:17:23 runnervmvrwv9 sudo[2401]: pam_unix(sudo:session): session closed for user root
2026-08-04T15:25:57.7565118Z Aug 04 15:17:23 runnervmvrwv9 sudo[2467]:     root : *** ; USER=root ; COMMAND=/usr/bin/systemctl restart docker
2026-08-04T15:25:57.7565836Z Aug 04 15:17:23 runnervmvrwv9 sudo[2467]: pam_unix(sudo:session): session opened for user root(uid=0) by (uid=0)
2026-08-04T15:25:57.7566478Z Aug 04 15:17:24 runnervmvrwv9 sudo[2467]: pam_unix(sudo:session): session closed for user root
2026-08-04T15:25:57.7567447Z Aug 04 15:17:24 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:24 INFO Fetching custom detection rules module=armour api_url=https://agent.api.stepsecurity.io/v1 repo=Stirling-Tools/Stirling-PDF
2026-08-04T15:25:57.7568722Z Aug 04 15:17:24 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:24 INFO Custom detection rules evaluator initialized module=armour
2026-08-04T15:25:57.7569662Z Aug 04 15:17:24 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:24 INFO Detection manager started module=detection-manager workers=4 buffer_size=1000
2026-08-04T15:25:57.7570820Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Selected Armour variant module=armour variant=fmod_ret
2026-08-04T15:25:57.7571639Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Config module=armour ENFORCE_WRITE_BLOCK=false
2026-08-04T15:25:57.7572407Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Config module=armour ENFORCE_KILL_BLOCK=true
2026-08-04T15:25:57.7573130Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Config module=armour AGENT_PID=2360
2026-08-04T15:25:57.7573840Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Config module=armour ENFORCE_READ_BLOCK=false
2026-08-04T15:25:57.7574535Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Map size module=armour protected_pids=1
2026-08-04T15:25:57.7575253Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Map size module=armour protected_pid_inodes=1
2026-08-04T15:25:57.7576629Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Map size module=armour protected_bpf_ids=9
2026-08-04T15:25:57.7577808Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Map size module=armour protected_fs_inodes=6
2026-08-04T15:25:57.7578831Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Map size module=armour protected_proc_fs_inodes=2
2026-08-04T15:25:57.7579536Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Map size module=armour events=16384
2026-08-04T15:25:57.7580433Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO ProtectedPids module=armour pids=map[2361:2360]
2026-08-04T15:25:57.7581185Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO ProtectedBPFIDs module=armour ids="[18 16 12 19 17]"
2026-08-04T15:25:57.7582009Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO File Info module=armour inoKey="{Device:24 Inode:17061}" path=/proc/2225/mem
2026-08-04T15:25:57.7582884Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO File Info module=armour inoKey="{Device:24 Inode:17062}" path=/proc/2204/mem
2026-08-04T15:25:57.7583766Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO File Info module=armour inoKey="{Device:2049 Inode:89486}" path=/etc/sudoers.d/runner
2026-08-04T15:25:57.7584657Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO File Info module=armour inoKey="{Device:28 Inode:959}" path=/etc/resolv.conf
2026-08-04T15:25:57.7585555Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO File Info module=armour inoKey="{Device:2049 Inode:508}" path=/etc/systemd/resolved.conf
2026-08-04T15:25:57.7586489Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO File Info module=armour inoKey="{Device:2049 Inode:291419}" path=/etc/docker/daemon.json
2026-08-04T15:25:57.7587316Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Protection maps populated module=armour
2026-08-04T15:25:57.7588002Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Protection maps are freezed module=armour
2026-08-04T15:25:57.7588669Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Linking completed module=armour
2026-08-04T15:25:57.7589304Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Armour engaged module=armour
2026-08-04T15:25:57.7590127Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO RingBuffer created module=armour size=16384
2026-08-04T15:25:57.7591066Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO Listening for events module=armour
2026-08-04T15:25:57.7591803Z Aug 04 15:17:25 runnervmvrwv9 agentservice[2360]: 2026/08/04 15:17:25 INFO [LOCKDOWN] Runner.Worker PID set module=armour pid=2225
2026-08-04T15:25:57.7592252Z 
2026-08-04T15:25:57.7677238Z Cleaning up orphan processes
2026-08-04T15:25:57.8056696Z Terminate orphan process: pid (3117) (java)
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 3. `agno-agi__agno__096352887725.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/agno-agi__agno__096352887725.txt` (authoritative; read this, not the excerpt)
- **Repository**: `agno-agi/agno`
- **Content hash (sha256, first 16)**: `6c24a57a5bbb169b`
- **Body size**: 60,966 bytes, 750 lines
- **Excerpt**: final 120 of 750 lines, content-blind

```text
2026-08-20T07:44:15.9058830Z Using cached mypy-2.1.0-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (15.0 MB)
2026-08-20T07:44:15.9124936Z Using cached pytest-9.1.1-py3-none-any.whl (386 kB)
2026-08-20T07:44:15.9139728Z Using cached ruff-0.15.20-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (11.5 MB)
2026-08-20T07:44:15.9215068Z Downloading ast_serialize-0.8.0-cp39-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (1.3 MB)
2026-08-20T07:44:15.9431915Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.3/1.3 MB 65.4 MB/s  0:00:00
2026-08-20T07:44:15.9446645Z Using cached pluggy-1.6.0-py3-none-any.whl (20 kB)
2026-08-20T07:44:15.9483746Z Downloading questionary-2.1.1-py3-none-any.whl (36 kB)
2026-08-20T07:44:15.9541151Z Downloading prompt_toolkit-3.0.53-py3-none-any.whl (392 kB)
2026-08-20T07:44:15.9594468Z Using cached exceptiongroup-1.3.1-py3-none-any.whl (16 kB)
2026-08-20T07:44:15.9607603Z Using cached iniconfig-2.3.0-py3-none-any.whl (7.5 kB)
2026-08-20T07:44:15.9668524Z Downloading librt-0.15.0-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (515 kB)
2026-08-20T07:44:15.9714976Z Using cached mypy_extensions-1.1.0-py3-none-any.whl (5.0 kB)
2026-08-20T07:44:15.9750473Z Downloading packaging-26.3-py3-none-any.whl (129 kB)
2026-08-20T07:44:15.9787117Z Using cached pathspec-1.1.1-py3-none-any.whl (57 kB)
2026-08-20T07:44:15.9826188Z Downloading pygments-2.21.0-py3-none-any.whl (1.3 MB)
2026-08-20T07:44:15.9897697Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.3/1.3 MB 223.8 MB/s  0:00:00
2026-08-20T07:44:15.9912120Z Using cached tomli-2.4.1-py3-none-any.whl (14 kB)
2026-08-20T07:44:15.9926159Z Using cached typing_extensions-4.16.0-py3-none-any.whl (45 kB)
2026-08-20T07:44:15.9963843Z Downloading wcwidth-0.8.2-py3-none-any.whl (323 kB)
2026-08-20T07:44:16.0003958Z Using cached httpx-0.28.1-py3-none-any.whl (73 kB)
2026-08-20T07:44:16.0017287Z Using cached httpcore-1.0.9-py3-none-any.whl (78 kB)
2026-08-20T07:44:16.0030976Z Using cached h11-0.16.0-py3-none-any.whl (37 kB)
2026-08-20T07:44:16.0044903Z Using cached anyio-4.14.2-py3-none-any.whl (125 kB)
2026-08-20T07:44:16.0081504Z Downloading idna-3.19-py3-none-any.whl (68 kB)
2026-08-20T07:44:16.0116339Z Using cached certifi-2026.7.22-py3-none-any.whl (136 kB)
2026-08-20T07:44:16.0130068Z Using cached rich-15.0.0-py3-none-any.whl (310 kB)
2026-08-20T07:44:16.0144284Z Using cached markdown_it_py-4.2.0-py3-none-any.whl (91 kB)
2026-08-20T07:44:16.0157582Z Using cached mdurl-0.1.2-py3-none-any.whl (10.0 kB)
2026-08-20T07:44:16.0193020Z Downloading typer-0.27.1-py3-none-any.whl (122 kB)
2026-08-20T07:44:16.0248182Z Using cached annotated_doc-0.0.5-py3-none-any.whl (5.3 kB)
2026-08-20T07:44:16.0261426Z Using cached shellingham-1.5.4-py2.py3-none-any.whl (9.8 kB)
2026-08-20T07:44:16.1485081Z Building wheels for collected packages: agnoctl
2026-08-20T07:44:16.1494372Z   Building editable for agnoctl (pyproject.toml): started
2026-08-20T07:44:16.3564477Z   Building editable for agnoctl (pyproject.toml): finished with status 'done'
2026-08-20T07:44:16.3570685Z   Created wheel for agnoctl: filename=agnoctl-0.1.3-0.editable-py3-none-any.whl size=12032 sha256=b65fd86f35d38915d3b1c97ca9b80d5403137f0477a02170332067f534aced13
2026-08-20T07:44:16.3572392Z   Stored in directory: /tmp/pip-ephem-wheel-cache-s9ccsk14/wheels/bb/32/63/58fd3f8131e30fc0783d224f04fd8e58296e0fc8b1212f2f9e
2026-08-20T07:44:16.3591247Z Successfully built agnoctl
2026-08-20T07:44:16.4252090Z Installing collected packages: wcwidth, typing_extensions, tomli, shellingham, ruff, pygments, pluggy, pathspec, packaging, mypy_extensions, mdurl, librt, iniconfig, idna, h11, certifi, ast-serialize, annotated-doc, prompt_toolkit, mypy, markdown-it-py, httpcore, exceptiongroup, rich, questionary, pytest, anyio, typer, httpx, agnoctl
2026-08-20T07:44:20.2706878Z 
2026-08-20T07:44:20.2746544Z Successfully installed agnoctl-0.1.3 annotated-doc-0.0.5 anyio-4.14.2 ast-serialize-0.8.0 certifi-2026.7.22 exceptiongroup-1.3.1 h11-0.16.0 httpcore-1.0.9 httpx-0.28.1 idna-3.19 iniconfig-2.3.0 librt-0.15.0 markdown-it-py-4.2.0 mdurl-0.1.2 mypy-2.1.0 mypy_extensions-1.1.0 packaging-26.3 pathspec-1.1.1 pluggy-1.6.0 prompt_toolkit-3.0.53 pygments-2.21.0 pytest-9.1.1 questionary-2.1.1 rich-15.0.0 ruff-0.15.20 shellingham-1.5.4 tomli-2.4.1 typer-0.27.1 typing_extensions-4.16.0 wcwidth-0.8.2
2026-08-20T07:44:20.3869493Z ##[group]Run ruff check .
2026-08-20T07:44:20.3869800Z [36;1mruff check .[0m
2026-08-20T07:44:20.3912051Z shell: /usr/bin/bash -e {0}
2026-08-20T07:44:20.3912331Z env:
2026-08-20T07:44:20.3912620Z   pythonLocation: /opt/hostedtoolcache/Python/3.10.20/x64
2026-08-20T07:44:20.3913084Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.10.20/x64/lib/pkgconfig
2026-08-20T07:44:20.3913532Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-08-20T07:44:20.3914121Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-08-20T07:44:20.3914510Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-08-20T07:44:20.3914900Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.10.20/x64/lib
2026-08-20T07:44:20.3915247Z ##[endgroup]
2026-08-20T07:44:20.4100282Z All checks passed!
2026-08-20T07:44:20.4138024Z ##[group]Run mypy . --config-file pyproject.toml
2026-08-20T07:44:20.4138637Z [36;1mmypy . --config-file pyproject.toml[0m
2026-08-20T07:44:20.4178778Z shell: /usr/bin/bash -e {0}
2026-08-20T07:44:20.4179057Z env:
2026-08-20T07:44:20.4179344Z   pythonLocation: /opt/hostedtoolcache/Python/3.10.20/x64
2026-08-20T07:44:20.4179806Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.10.20/x64/lib/pkgconfig
2026-08-20T07:44:20.4180249Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-08-20T07:44:20.4180658Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-08-20T07:44:20.4181076Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-08-20T07:44:20.4181467Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.10.20/x64/lib
2026-08-20T07:44:20.4181804Z ##[endgroup]
2026-08-20T07:44:24.8382999Z Success: no issues found in 21 source files
2026-08-20T07:44:24.8559269Z ##[group]Run python -m pytest ./tests
2026-08-20T07:44:24.8559615Z [36;1mpython -m pytest ./tests[0m
2026-08-20T07:44:24.8600005Z shell: /usr/bin/bash -e {0}
2026-08-20T07:44:24.8600275Z env:
2026-08-20T07:44:24.8600557Z   pythonLocation: /opt/hostedtoolcache/Python/3.10.20/x64
2026-08-20T07:44:24.8601008Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.10.20/x64/lib/pkgconfig
2026-08-20T07:44:24.8601442Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-08-20T07:44:24.8601828Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-08-20T07:44:24.8602213Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-08-20T07:44:24.8602599Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.10.20/x64/lib
2026-08-20T07:44:24.8602957Z ##[endgroup]
2026-08-20T07:44:26.3697159Z ============================= test session starts ==============================
2026-08-20T07:44:26.3697702Z platform linux -- Python 3.10.20, pytest-9.1.1, pluggy-1.6.0
2026-08-20T07:44:26.3698192Z rootdir: /home/runner/work/agno/agno/libs/agnoctl
2026-08-20T07:44:26.3699770Z configfile: pyproject.toml
2026-08-20T07:44:26.3700029Z plugins: anyio-4.14.2
2026-08-20T07:44:26.3700261Z collected 344 items
2026-08-20T07:44:26.3700400Z 
2026-08-20T07:44:26.4695967Z tests/test_adapters.py ................................................. [ 14%]
2026-08-20T07:44:26.4836892Z .......                                                                  [ 16%]
2026-08-20T07:44:26.5130426Z tests/test_claude_desktop.py ..............                              [ 20%]
2026-08-20T07:44:27.0279889Z tests/test_connect_cmd.py .............................................. [ 33%]
2026-08-20T07:44:27.2346629Z ....................                                                     [ 39%]
2026-08-20T07:44:29.1489452Z tests/test_create_lifecycle.py ......................................... [ 51%]
2026-08-20T07:44:29.2859880Z ............................                                             [ 59%]
2026-08-20T07:44:29.5675737Z tests/test_disconnect_cmd.py .........................                   [ 66%]
2026-08-20T07:44:29.6451468Z tests/test_discovery.py .....................................            [ 77%]
2026-08-20T07:44:29.6760881Z tests/test_main.py ....                                                  [ 78%]
2026-08-20T07:44:29.6919921Z tests/test_mcp_client.py ..........                                      [ 81%]
2026-08-20T07:44:29.7202331Z tests/test_security.py .......................................           [ 93%]
2026-08-20T07:44:29.7470014Z tests/test_status_cmd.py ...                                             [ 93%]
2026-08-20T07:44:29.9582655Z tests/test_tokens_cmd.py .....................                           [100%]
2026-08-20T07:44:29.9583661Z 
2026-08-20T07:44:29.9583913Z ============================= 344 passed in 4.44s ==============================
2026-08-20T07:44:30.0441136Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-08-20T07:44:30.0442320Z Post job cleanup.
2026-08-20T07:44:30.1688904Z Cache hit occurred on the primary key setup-python-Linux-24.04-Ubuntu-python-3.10.20-pip-02800bd8c2c2b72a3c51ab0caea6aeb5c2ca083ad4867f939181bef45cb0531a, not saving cache.
2026-08-20T07:44:30.1690608Z (node:2405) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-08-20T07:44:30.1691308Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-08-20T07:44:30.1852498Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-08-20T07:44:30.1853675Z Post job cleanup.
2026-08-20T07:44:30.2560240Z (node:2413) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-08-20T07:44:30.2561005Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-08-20T07:44:30.2589597Z [command]/usr/bin/git version
2026-08-20T07:44:30.2625480Z git version 2.54.0
2026-08-20T07:44:30.2662697Z Temporarily overriding HOME='/home/runner/work/_temp/bb3c065f-da20-4be1-9a55-2a7b0ba329a0' before making global git config changes
2026-08-20T07:44:30.2664079Z Adding repository directory to the temporary git global config as a safe directory
2026-08-20T07:44:30.2667845Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/agno/agno
2026-08-20T07:44:30.2702939Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-08-20T07:44:30.2733773Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-08-20T07:44:30.2981547Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-08-20T07:44:30.3007727Z http.https://github.com/.extraheader
2026-08-20T07:44:30.3018152Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-08-20T07:44:30.3050882Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-08-20T07:44:30.3444289Z Cleaning up orphan processes
2026-08-20T07:44:30.3721802Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/checkout@v3, actions/setup-python@v4. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 4. `apache__atlas__092533695478.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/apache__atlas__092533695478.txt` (authoritative; read this, not the excerpt)
- **Repository**: `apache/atlas`
- **Content hash (sha256, first 16)**: `b9e8b32992648d8e`
- **Body size**: 329,520 bytes, 3,359 lines
- **Excerpt**: final 120 of 3,359 lines, content-blind

```text
2026-08-06T06:33:34.8762549Z     "{"requestedCount":1,"purgedCount":0,"purgedDependenciesCount":0,"failedCount":0,"failedDependenciesCount":0,"skippedCount":0,"validGuidCount":1,"executionFailed":true,"expandedEntityCount":0,"skippedRequestedCount":0,"skippedDependenciesCount":0,"unprocessedCount":0,"batchCount":0,"runId":"479aa91c-b5f4-4cfd-9826-d3edbca73a52"}",
2026-08-06T06:33:34.8763874Z     0L,
2026-08-06T06:33:34.8764086Z     "479aa91c-b5f4-4cfd-9826-d3edbca73a52",
2026-08-06T06:33:34.8764359Z     SUMMARY
2026-08-06T06:33:34.8764527Z );
2026-08-06T06:33:34.8764919Z -> at org.apache.atlas.services.PurgeAuditWriter.writeSummary(PurgeAuditWriter.java:115)
2026-08-06T06:33:34.8765327Z 
2026-08-06T06:33:34.8765401Z [INFO] 
2026-08-06T06:33:34.8765670Z [ERROR] Tests run: 2500, Failures: 2, Errors: 0, Skipped: 16
2026-08-06T06:33:34.8765979Z [INFO] 
2026-08-06T06:33:34.9125232Z [INFO] ------------------------------------------------------------------------
2026-08-06T06:33:34.9126506Z [INFO] Reactor Summary for apache-atlas 3.0.0-SNAPSHOT:
2026-08-06T06:33:34.9127250Z [INFO] 
2026-08-06T06:33:34.9128016Z [INFO] Apache Atlas Server Build Tools .................... SUCCESS [  0.713 s]
2026-08-06T06:33:34.9148357Z [INFO] apache-atlas ....................................... SUCCESS [  2.785 s]
2026-08-06T06:33:34.9149281Z [INFO] Apache Atlas Integration ........................... SUCCESS [02:34 min]
2026-08-06T06:33:34.9150187Z [INFO] Apache Atlas Client ................................ SUCCESS [  0.320 s]
2026-08-06T06:33:34.9151487Z [INFO] atlas-client-common ................................ SUCCESS [  4.948 s]
2026-08-06T06:33:34.9152361Z [INFO] atlas-client-v2 .................................... SUCCESS [  9.398 s]
2026-08-06T06:33:34.9153207Z [INFO] Apache Atlas Common ................................ SUCCESS [ 16.190 s]
2026-08-06T06:33:34.9154068Z [INFO] atlas-client-v1 .................................... SUCCESS [ 14.339 s]
2026-08-06T06:33:34.9154943Z [INFO] Apache Atlas Notification .......................... SUCCESS [01:00 min]
2026-08-06T06:33:34.9155831Z [INFO] Apache Atlas Couchbase Bridge ...................... SUCCESS [ 12.153 s]
2026-08-06T06:33:34.9157017Z [INFO] Apache Atlas Plugin Classloader .................... SUCCESS [  4.329 s]
2026-08-06T06:33:34.9157968Z [INFO] Apache Atlas Hive Bridge Shim ...................... SUCCESS [  4.423 s]
2026-08-06T06:33:34.9158892Z [INFO] Apache Atlas Graph Database Projects ............... SUCCESS [  0.247 s]
2026-08-06T06:33:34.9160118Z [INFO] Apache Atlas Graph Database API .................... SUCCESS [  4.270 s]
2026-08-06T06:33:34.9161014Z [INFO] Graph Database Common Code ......................... SUCCESS [  4.022 s]
2026-08-06T06:33:34.9161909Z [INFO] HBase shaded client with fix ....................... SUCCESS [ 19.332 s]
2026-08-06T06:33:34.9178406Z [INFO] JanusGraph RDBMS backend store ..................... SUCCESS [  5.572 s]
2026-08-06T06:33:34.9179397Z [INFO] Apache Atlas Test Utility Tools .................... SUCCESS [  5.615 s]
2026-08-06T06:33:34.9180359Z [INFO] Apache Atlas JanusGraph DB Impl .................... SUCCESS [01:51 min]
2026-08-06T06:33:34.9181350Z [INFO] Apache Atlas Graph Database Implementation Dependencies SUCCESS [  1.496 s]
2026-08-06T06:33:34.9182283Z [INFO] Apache Atlas Server API ............................ SUCCESS [  8.256 s]
2026-08-06T06:33:34.9183075Z [INFO] Apache Atlas Authorization ......................... SUCCESS [  8.382 s]
2026-08-06T06:33:34.9183886Z [INFO] Apache Atlas Repository ............................ FAILURE [24:23 min]
2026-08-06T06:33:34.9184607Z [INFO] Apache Atlas Authentication ........................ SKIPPED
2026-08-06T06:33:34.9185248Z [INFO] Apache Atlas React UI .............................. SKIPPED
2026-08-06T06:33:34.9185860Z [INFO] Apache Atlas UI .................................... SKIPPED
2026-08-06T06:33:34.9186779Z [INFO] Apache Atlas Server Common ......................... SKIPPED
2026-08-06T06:33:34.9187465Z [INFO] Apache Atlas Web Application ....................... SKIPPED
2026-08-06T06:33:34.9188100Z [INFO] Apache Atlas Hive Bridge ........................... SKIPPED
2026-08-06T06:33:34.9188725Z [INFO] Apache Atlas Falcon Bridge Shim .................... SKIPPED
2026-08-06T06:33:34.9189349Z [INFO] Apache Atlas Falcon Bridge ......................... SKIPPED
2026-08-06T06:33:34.9189980Z [INFO] Apache Atlas Hbase Bridge Shim ..................... SKIPPED
2026-08-06T06:33:34.9190626Z [INFO] Apache Atlas Hbase Bridge .......................... SKIPPED
2026-08-06T06:33:34.9191284Z [INFO] Apache HBase - Testing Util ........................ SKIPPED
2026-08-06T06:33:34.9191951Z [INFO] Apache Atlas FileSystem Model ...................... SKIPPED
2026-08-06T06:33:34.9192585Z [INFO] Apache Atlas Impala Hook API ....................... SKIPPED
2026-08-06T06:33:34.9193220Z [INFO] Apache Atlas Impala Bridge Shim .................... SKIPPED
2026-08-06T06:33:34.9193846Z [INFO] Apache Atlas Impala Bridge ......................... SKIPPED
2026-08-06T06:33:34.9194487Z [INFO] Apache Atlas Kafka Bridge .......................... SKIPPED
2026-08-06T06:33:34.9195122Z [INFO] Apache Atlas Sqoop Bridge Shim ..................... SKIPPED
2026-08-06T06:33:34.9195754Z [INFO] Apache Atlas Sqoop Bridge .......................... SKIPPED
2026-08-06T06:33:34.9196610Z [INFO] Apache Atlas Storm Bridge Shim ..................... SKIPPED
2026-08-06T06:33:34.9197265Z [INFO] Apache Atlas Storm Bridge .......................... SKIPPED
2026-08-06T06:33:34.9197912Z [INFO] Apache Atlas Trino Bridge .......................... SKIPPED
2026-08-06T06:33:34.9198886Z [INFO] atlas-examples ..................................... SKIPPED
2026-08-06T06:33:34.9199657Z [INFO] sample-app ......................................... SKIPPED
2026-08-06T06:33:34.9200418Z [INFO] Apache Atlas classification updater ................ SKIPPED
2026-08-06T06:33:34.9201051Z [INFO] Apache Atlas index repair tool ..................... SKIPPED
2026-08-06T06:33:34.9201717Z [INFO] Apache Atlas Notification Analyzer ................. SKIPPED
2026-08-06T06:33:34.9202360Z [INFO] Rest Notification Webapp ........................... SKIPPED
2026-08-06T06:33:34.9203104Z [INFO] Apache Atlas Distribution .......................... SKIPPED
2026-08-06T06:33:34.9203765Z [INFO] Apache Atlas Documentation ......................... SKIPPED
2026-08-06T06:33:34.9204830Z [INFO] ------------------------------------------------------------------------
2026-08-06T06:33:34.9205667Z [INFO] BUILD FAILURE
2026-08-06T06:33:34.9206156Z [INFO] ------------------------------------------------------------------------
2026-08-06T06:33:34.9207010Z [INFO] Total time:  31:58 min
2026-08-06T06:33:34.9207426Z [INFO] Finished at: 2026-08-06T06:33:34Z
2026-08-06T06:33:34.9207968Z [INFO] ------------------------------------------------------------------------
2026-08-06T06:33:34.9209243Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.5.3:test (default-test) on project atlas-repository: There are test failures.
2026-08-06T06:33:34.9210288Z [ERROR] 
2026-08-06T06:33:34.9211024Z [ERROR] See /home/runner/work/atlas/atlas/repository/target/surefire-reports for the individual test results.
2026-08-06T06:33:34.9212127Z [ERROR] See dump files (if any exist) [date].dump, [date]-jvmRun[N].dump and [date].dumpstream.
2026-08-06T06:33:34.9212791Z [ERROR] -> [Help 1]
2026-08-06T06:33:34.9213096Z [ERROR] 
2026-08-06T06:33:34.9213639Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-08-06T06:33:34.9214464Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-08-06T06:33:34.9215089Z [ERROR] 
2026-08-06T06:33:34.9215923Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-08-06T06:33:34.9217410Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
2026-08-06T06:33:34.9218114Z [ERROR] 
2026-08-06T06:33:34.9218770Z [ERROR] After correcting the problems, you can resume the build with the command
2026-08-06T06:33:34.9219531Z [ERROR]   mvn <args> -rf :atlas-repository
2026-08-06T06:33:34.9604438Z ##[error]Process completed with exit code 1.
2026-08-06T06:33:34.9745748Z Post job cleanup.
2026-08-06T06:33:35.1269959Z Post job cleanup.
2026-08-06T06:33:35.2212400Z [command]/usr/bin/git version
2026-08-06T06:33:35.2276944Z git version 2.54.0
2026-08-06T06:33:35.2328634Z Temporarily overriding HOME='/home/runner/work/_temp/7c9b1efb-eccd-452d-9c53-6669b7e25c70' before making global git config changes
2026-08-06T06:33:35.2330243Z Adding repository directory to the temporary git global config as a safe directory
2026-08-06T06:33:35.2331810Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/atlas/atlas
2026-08-06T06:33:35.2376065Z Removing SSH command configuration
2026-08-06T06:33:35.2385134Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-08-06T06:33:35.2436012Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-08-06T06:33:35.2808143Z Removing HTTP extra header
2026-08-06T06:33:35.2818630Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-08-06T06:33:35.2865812Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-08-06T06:33:35.3132612Z Removing includeIf entries pointing to credentials config files
2026-08-06T06:33:35.3141299Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-08-06T06:33:35.3200063Z includeif.gitdir:/home/runner/work/atlas/atlas/.git.path
2026-08-06T06:33:35.3201036Z includeif.gitdir:/home/runner/work/atlas/atlas/.git/worktrees/*.path
2026-08-06T06:33:35.3201891Z includeif.gitdir:/github/workspace/.git.path
2026-08-06T06:33:35.3202633Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-08-06T06:33:35.3211009Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/atlas/atlas/.git.path
2026-08-06T06:33:35.3235733Z /home/runner/work/_temp/git-credentials-2c9a307d-af19-4a80-b6c0-ed6494afb1d0.config
2026-08-06T06:33:35.3248132Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/atlas/atlas/.git.path /home/runner/work/_temp/git-credentials-2c9a307d-af19-4a80-b6c0-ed6494afb1d0.config
2026-08-06T06:33:35.3285955Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/atlas/atlas/.git/worktrees/*.path
2026-08-06T06:33:35.3311050Z /home/runner/work/_temp/git-credentials-2c9a307d-af19-4a80-b6c0-ed6494afb1d0.config
2026-08-06T06:33:35.3322175Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/atlas/atlas/.git/worktrees/*.path /home/runner/work/_temp/git-credentials-2c9a307d-af19-4a80-b6c0-ed6494afb1d0.config
2026-08-06T06:33:35.3358561Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-08-06T06:33:35.3381304Z /github/runner_temp/git-credentials-2c9a307d-af19-4a80-b6c0-ed6494afb1d0.config
2026-08-06T06:33:35.3389883Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git.path /github/runner_temp/git-credentials-2c9a307d-af19-4a80-b6c0-ed6494afb1d0.config
2026-08-06T06:33:35.3421444Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-08-06T06:33:35.3444238Z /github/runner_temp/git-credentials-2c9a307d-af19-4a80-b6c0-ed6494afb1d0.config
2026-08-06T06:33:35.3453985Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path /github/runner_temp/git-credentials-2c9a307d-af19-4a80-b6c0-ed6494afb1d0.config
2026-08-06T06:33:35.3487826Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-08-06T06:33:35.3727632Z Removing credentials config '/home/runner/work/_temp/git-credentials-2c9a307d-af19-4a80-b6c0-ed6494afb1d0.config'
2026-08-06T06:33:35.3876165Z Cleaning up orphan processes
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 5. `apache__beam__082969168132.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/apache__beam__082969168132.txt` (authoritative; read this, not the excerpt)
- **Repository**: `apache/beam`
- **Content hash (sha256, first 16)**: `ac36f75f37785845`
- **Body size**: 951,492 bytes, 7,303 lines
- **Excerpt**: final 120 of 7,303 lines, content-blind

```text
2026-06-23T14:35:03.2288842Z   github_token: ***
2026-06-23T14:35:03.2289646Z   github_retries: 10
2026-06-23T14:35:03.2290319Z   ssl_verify: true
2026-06-23T14:35:03.2291042Z   check_name: Test Results
2026-06-23T14:35:03.2291861Z   fail_on: test failures
2026-06-23T14:35:03.2292631Z   action_fail: false
2026-06-23T14:35:03.2293459Z   action_fail_on_inconclusive: false
2026-06-23T14:35:03.2294420Z   time_unit: seconds
2026-06-23T14:35:03.2295263Z   report_suite_logs: none
2026-06-23T14:35:03.2296094Z   ignore_runs: false
2026-06-23T14:35:03.2297124Z   check_run: true
2026-06-23T14:35:03.2297816Z   job_summary: true
2026-06-23T14:35:03.2298689Z   compare_to_earlier_commit: true
2026-06-23T14:35:03.2299637Z   pull_request_build: merge
2026-06-23T14:35:03.2300767Z   check_run_annotations: all tests, skipped tests
2026-06-23T14:35:03.2301883Z   seconds_between_github_reads: 0.25
2026-06-23T14:35:03.2302585Z   seconds_between_github_writes: 2.0
2026-06-23T14:35:03.2303472Z   json_thousands_separator:  
2026-06-23T14:35:03.2304346Z   json_suite_details: false
2026-06-23T14:35:03.2305196Z   json_test_case_results: false
2026-06-23T14:35:03.2306080Z   search_pull_requests: false
2026-06-23T14:35:03.2307398Z env:
2026-06-23T14:35:03.2307918Z   DEVELOCITY_ACCESS_KEY: 
2026-06-23T14:35:03.2308859Z   GRADLE_ENTERPRISE_CACHE_USERNAME: ***
2026-06-23T14:35:03.2309975Z   GRADLE_ENTERPRISE_CACHE_PASSWORD: ***
2026-06-23T14:35:03.2310937Z   ALLOYDB_PASSWORD: ***
2026-06-23T14:35:03.2312468Z   KUBELET_GCLOUD_CONFIG_PATH: /var/lib/kubelet/pods/99826fae-871f-4849-a028-4d9100a66f1e/volumes/kubernetes.io~empty-dir/gcloud
2026-06-23T14:35:03.2314068Z   pythonLocation: /opt/hostedtoolcache/Python/3.14.6/x64
2026-06-23T14:35:03.2315158Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.14.6/x64/lib/pkgconfig
2026-06-23T14:35:03.2317322Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.14.6/x64
2026-06-23T14:35:03.2318315Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.14.6/x64
2026-06-23T14:35:03.2320065Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.14.6/x64
2026-06-23T14:35:03.2320859Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.14.6/x64/lib
2026-06-23T14:35:03.2321649Z   JAVA_HOME: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/11.0.31-11/x64
2026-06-23T14:35:03.2322589Z   JAVA_HOME_11_X64: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/11.0.31-11/x64
2026-06-23T14:35:03.2323437Z   GRADLE_ACTION_ID: gradle/actions/setup-gradle
2026-06-23T14:35:03.2324055Z   GRADLE_USER_HOME: /home/runner/.gradle
2026-06-23T14:35:03.2324623Z   GRADLE_BUILD_ACTION_SETUP_COMPLETED: true
2026-06-23T14:35:03.2325591Z   DEVELOCITY_INJECTION_INIT_SCRIPT_NAME: gradle-actions.inject-develocity.init.gradle
2026-06-23T14:35:03.2326806Z   DEVELOCITY_INJECTION_CUSTOM_VALUE: gradle-actions
2026-06-23T14:35:03.2327460Z   GITHUB_DEPENDENCY_GRAPH_ENABLED: false
2026-06-23T14:35:03.2328069Z ##[endgroup]
2026-06-23T14:35:03.2772177Z ##[command]/usr/local/bin/docker run --name ghcrioenricomipublishunittestresultactionv2240_caea21 --label 6bbb30 --workdir /github/workspace --rm -e "DEVELOCITY_ACCESS_KEY" -e "GRADLE_ENTERPRISE_CACHE_USERNAME" -e "GRADLE_ENTERPRISE_CACHE_PASSWORD" -e "ALLOYDB_PASSWORD" -e "KUBELET_GCLOUD_CONFIG_PATH" -e "pythonLocation" -e "PKG_CONFIG_PATH" -e "Python_ROOT_DIR" -e "Python2_ROOT_DIR" -e "Python3_ROOT_DIR" -e "LD_LIBRARY_PATH" -e "JAVA_HOME" -e "JAVA_HOME_11_X64" -e "GRADLE_ACTION_ID" -e "GRADLE_USER_HOME" -e "GRADLE_BUILD_ACTION_SETUP_COMPLETED" -e "DEVELOCITY_INJECTION_INIT_SCRIPT_NAME" -e "DEVELOCITY_INJECTION_CUSTOM_VALUE" -e "GITHUB_DEPENDENCY_GRAPH_ENABLED" -e "INPUT_COMMIT" -e "INPUT_COMMENT_MODE" -e "INPUT_FILES" -e "INPUT_LARGE_FILES" -e "INPUT_GITHUB_TOKEN" -e "INPUT_GITHUB_TOKEN_ACTOR" -e "INPUT_GITHUB_RETRIES" -e "INPUT_SSL_VERIFY" -e "INPUT_CHECK_NAME" -e "INPUT_COMMENT_TITLE" -e "INPUT_FAIL_ON" -e "INPUT_ACTION_FAIL" -e "INPUT_ACTION_FAIL_ON_INCONCLUSIVE" -e "INPUT_JUNIT_FILES" -e "INPUT_NUNIT_FILES" -e "INPUT_XUNIT_FILES" -e "INPUT_TRX_FILES" -e "INPUT_TIME_UNIT" -e "INPUT_TEST_FILE_PREFIX" -e "INPUT_REPORT_INDIVIDUAL_RUNS" -e "INPUT_REPORT_SUITE_LOGS" -e "INPUT_DEDUPLICATE_CLASSES_BY_FILE_NAME" -e "INPUT_IGNORE_RUNS" -e "INPUT_CHECK_RUN" -e "INPUT_JOB_SUMMARY" -e "INPUT_COMPARE_TO_EARLIER_COMMIT" -e "INPUT_PULL_REQUEST_BUILD" -e "INPUT_EVENT_FILE" -e "INPUT_EVENT_NAME" -e "INPUT_TEST_CHANGES_LIMIT" -e "INPUT_CHECK_RUN_ANNOTATIONS" -e "INPUT_CHECK_RUN_ANNOTATIONS_BRANCH" -e "INPUT_SECONDS_BETWEEN_GITHUB_READS" -e "INPUT_SECONDS_BETWEEN_GITHUB_WRITES" -e "INPUT_SECONDARY_RATE_LIMIT_WAIT_SECONDS" -e "INPUT_JSON_FILE" -e "INPUT_JSON_THOUSANDS_SEPARATOR" -e "INPUT_JSON_SUITE_DETAILS" -e "INPUT_JSON_TEST_CASE_RESULTS" -e "INPUT_SEARCH_PULL_REQUESTS" -e "HOME" -e "GITHUB_JOB" -e "GITHUB_REF" -e "GITHUB_SHA" -e "GITHUB_REPOSITORY" -e "GITHUB_REPOSITORY_OWNER" -e "GITHUB_REPOSITORY_OWNER_ID" -e "GITHUB_RUN_ID" -e "GITHUB_RUN_NUMBER" -e "GITHUB_RETENTION_DAYS" -e "GITHUB_RUN_ATTEMPT" -e "GITHUB_ACTOR_ID" -e "GITHUB_ACTOR" -e "GITHUB_WORKFLOW" -e "GITHUB_HEAD_REF" -e "GITHUB_BASE_REF" -e "GITHUB_EVENT_NAME" -e "GITHUB_SERVER_URL" -e "GITHUB_API_URL" -e "GITHUB_GRAPHQL_URL" -e "GITHUB_REF_NAME" -e "GITHUB_REF_PROTECTED" -e "GITHUB_REF_TYPE" -e "GITHUB_WORKFLOW_REF" -e "GITHUB_WORKFLOW_SHA" -e "GITHUB_REPOSITORY_ID" -e "GITHUB_TRIGGERING_ACTOR" -e "GITHUB_WORKSPACE" -e "GITHUB_EVENT_PATH" -e "GITHUB_PATH" -e "GITHUB_ENV" -e "GITHUB_STEP_SUMMARY" -e "GITHUB_STATE" -e "GITHUB_OUTPUT" -e "GITHUB_ACTION" -e "GITHUB_ACTION_REPOSITORY" -e "GITHUB_ACTION_REF" -e "RUNNER_OS" -e "RUNNER_ARCH" -e "RUNNER_NAME" -e "RUNNER_ENVIRONMENT" -e "RUNNER_TOOL_CACHE" -e "RUNNER_TEMP" -e "RUNNER_WORKSPACE" -e "ACTIONS_RUNTIME_URL" -e "ACTIONS_RUNTIME_TOKEN" -e "ACTIONS_CACHE_URL" -e "ACTIONS_RESULTS_URL" -e "ACTIONS_ORCHESTRATION_ID" -e GITHUB_ACTIONS=true -e CI=true -v "/var/run/docker.sock":"/var/run/docker.sock" -v "/runner/_work/_temp":"/github/runner_temp" -v "/runner/_work/_temp/_github_home":"/github/home" -v "/runner/_work/_temp/_github_workflow":"/github/workflow" -v "/runner/_work/_temp/_runner_file_commands":"/github/file_commands" -v "/runner/_work/beam/beam":"/github/workspace" ghcr.io/enricomi/publish-unit-test-result-action:v2.24.0
2026-06-23T14:35:07.5195628Z 2026-06-23 14:35:07 +0000 - publish -  INFO - Available memory to read files: 43.4 GiB
2026-06-23T14:35:08.2525100Z 2026-06-23 14:35:08 +0000 - publish -  INFO - Reading files **/pytest*.xml (4 files, 334.6 KiB)
2026-06-23T14:35:08.2737740Z 2026-06-23 14:35:08 +0000 - publish -  INFO - Detected 4 JUnit XML files (334.6 KiB)
2026-06-23T14:35:08.2739974Z 2026-06-23 14:35:08 +0000 - publish -  INFO - Finished reading 4 files in 0.02 seconds
2026-06-23T14:35:08.8046549Z 2026-06-23 14:35:08 +0000 - publish -  INFO - Publishing failure results for commit 9595ee208aa66f198502d4f32243123dd641357e
2026-06-23T14:35:12.3053698Z 2026-06-23 14:35:12 +0000 - publish -  INFO - Created check https://github.com/apache/beam/runs/82981885601
2026-06-23T14:35:12.3113775Z 2026-06-23 14:35:12 +0000 - publish -  INFO - Created job summary
2026-06-23T14:35:12.3115653Z 2026-06-23 14:35:12 +0000 - publish -  INFO - Commenting on pull requests disabled
2026-06-23T14:35:12.8413777Z Post job cleanup.
2026-06-23T14:35:12.8836282Z Post job cleanup.
2026-06-23T14:35:13.6006572Z In post-action step
2026-06-23T14:35:13.6032885Z Enhanced Caching: This build is using the proprietary 'gradle-actions-caching' provider for optimized caching support. See https://github.com/gradle/actions/blob/main/DISTRIBUTION.md for terms of use and opt-out instructions.
2026-06-23T14:35:13.8229474Z ##[group]Stopping Gradle daemons
2026-06-23T14:35:13.8231141Z Stopping Gradle daemons for /home/runner/.gradle/wrapper/dists/gradle-8.14.3-bin/cv11ve7ro1n3o1j4so8xd9n66/gradle-8.14.3
2026-06-23T14:35:13.8264236Z [command]/home/runner/.gradle/wrapper/dists/gradle-8.14.3-bin/cv11ve7ro1n3o1j4so8xd9n66/gradle-8.14.3/bin/gradle --stop
2026-06-23T14:35:16.9291576Z No Gradle daemons are running.
2026-06-23T14:35:16.9625584Z ##[endgroup]
2026-06-23T14:35:16.9627408Z Not performing cache-cleanup due to build failure
2026-06-23T14:35:16.9629564Z ##[group]Caching Gradle state
2026-06-23T14:35:18.5454849Z [command]/usr/bin/tar --posix -cf cache.tgz --exclude cache.tgz -P -C /runner/_work/beam/beam --files-from manifest.txt -z
2026-06-23T14:35:18.6343339Z [command]/usr/bin/tar --posix -cf cache.tgz --exclude cache.tgz -P -C /runner/_work/beam/beam --files-from manifest.txt -z
2026-06-23T14:35:19.2150934Z Sent 159645 of 159645 (100.0%), 0.5 MBs/sec
2026-06-23T14:35:19.3907562Z Saved cache entry with key gradle-instrumented-jars-v1-91100949ff16bbdc89eb6e4c371591a9 from /home/runner/.gradle/caches/jars-*/*/ in 945ms
2026-06-23T14:35:20.0117330Z Sent 402611 of 402611 (100.0%), 0.5 MBs/sec
2026-06-23T14:35:20.2172741Z Saved cache entry with key gradle-groovy-dsl-v1-0cf7921b59bc4fa1c34dccea36327126 from /home/runner/.gradle/caches/*/groovy-dsl/*/ in 1642ms
2026-06-23T14:35:20.2882102Z [command]/usr/bin/tar --posix -cf cache.tgz --exclude cache.tgz -P -C /runner/_work/beam/beam --files-from manifest.txt -z
2026-06-23T14:35:54.0989811Z Sent 0 of 169952695 (0.0%), 0.0 MBs/sec
2026-06-23T14:35:54.6955986Z Sent 169952695 of 169952695 (100.0%), 101.5 MBs/sec
2026-06-23T14:35:54.9891738Z Saved cache entry with key gradle-home-v1|Linux-X64|beam_PreCommit_Python_Transforms[cb029ce181e3cc2e0d58be3388e76b07]-c77b2d40626fcf68282d1aa19cd0c30af0e941ef from /home/runner/.gradle/caches,/home/runner/.gradle/notifications,/home/runner/.gradle/.setup-gradle in 34721ms
2026-06-23T14:35:54.9897422Z ##[endgroup]
2026-06-23T14:35:54.9918825Z Generating Job Summary
2026-06-23T14:35:54.9999257Z Completed post-action step
2026-06-23T14:35:55.0558745Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-23T14:35:55.0561664Z Post job cleanup.
2026-06-23T14:35:55.4087195Z (node:56053) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-06-23T14:35:55.4091180Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-06-23T14:35:55.4534307Z Post job cleanup.
2026-06-23T14:35:55.4762699Z Post job cleanup.
2026-06-23T14:35:55.6823013Z [command]/usr/bin/git version
2026-06-23T14:35:55.6919118Z git version 2.54.0
2026-06-23T14:35:55.7055313Z Temporarily overriding HOME='/runner/_work/_temp/2ee0c31d-bb79-4755-9a85-cb87c7abbed5' before making global git config changes
2026-06-23T14:35:55.7058388Z Adding repository directory to the temporary git global config as a safe directory
2026-06-23T14:35:55.7070365Z [command]/usr/bin/git config --global --add safe.directory /runner/_work/beam/beam
2026-06-23T14:35:55.7150467Z Removing SSH command configuration
2026-06-23T14:35:55.7166929Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-06-23T14:35:55.7255760Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-06-23T14:35:55.7992988Z Removing HTTP extra header
2026-06-23T14:35:55.8005528Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-06-23T14:35:55.8102582Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-06-23T14:35:55.8795613Z Removing includeIf entries pointing to credentials config files
2026-06-23T14:35:55.8816851Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-06-23T14:35:55.8885130Z includeif.gitdir:/runner/_work/beam/beam/.git.path
2026-06-23T14:35:55.8887764Z includeif.gitdir:/runner/_work/beam/beam/.git/worktrees/*.path
2026-06-23T14:35:55.8889132Z includeif.gitdir:/github/workspace/.git.path
2026-06-23T14:35:55.8890578Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-06-23T14:35:55.8912508Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/runner/_work/beam/beam/.git.path
2026-06-23T14:35:55.8974350Z /runner/_work/_temp/git-credentials-2506dfab-ba11-4ad2-ae7c-8eff303756a6.config
2026-06-23T14:35:55.9014663Z [command]/usr/bin/git config --local --unset includeif.gitdir:/runner/_work/beam/beam/.git.path /runner/_work/_temp/git-credentials-2506dfab-ba11-4ad2-ae7c-8eff303756a6.config
2026-06-23T14:35:55.9113240Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/runner/_work/beam/beam/.git/worktrees/*.path
2026-06-23T14:35:55.9177924Z /runner/_work/_temp/git-credentials-2506dfab-ba11-4ad2-ae7c-8eff303756a6.config
2026-06-23T14:35:55.9217394Z [command]/usr/bin/git config --local --unset includeif.gitdir:/runner/_work/beam/beam/.git/worktrees/*.path /runner/_work/_temp/git-credentials-2506dfab-ba11-4ad2-ae7c-8eff303756a6.config
2026-06-23T14:35:55.9312487Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-06-23T14:35:55.9385490Z /github/runner_temp/git-credentials-2506dfab-ba11-4ad2-ae7c-8eff303756a6.config
2026-06-23T14:35:55.9418089Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git.path /github/runner_temp/git-credentials-2506dfab-ba11-4ad2-ae7c-8eff303756a6.config
2026-06-23T14:35:55.9524691Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-06-23T14:35:55.9588996Z /github/runner_temp/git-credentials-2506dfab-ba11-4ad2-ae7c-8eff303756a6.config
2026-06-23T14:35:55.9619058Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path /github/runner_temp/git-credentials-2506dfab-ba11-4ad2-ae7c-8eff303756a6.config
2026-06-23T14:35:55.9718462Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-06-23T14:35:56.0437275Z Removing credentials config '/runner/_work/_temp/git-credentials-2506dfab-ba11-4ad2-ae7c-8eff303756a6.config'
2026-06-23T14:35:56.0690071Z A job completed hook has been configured by the self-hosted runner administrator
2026-06-23T14:35:56.0741404Z ##[group]Run '/etc/arc/hooks/job-completed.sh'
2026-06-23T14:35:56.0761595Z shell: /usr/bin/bash --noprofile --norc -e -o pipefail {0}
2026-06-23T14:35:56.0762344Z ##[endgroup]
2026-06-23T14:35:56.0883371Z [0;37m2026-06-23 14:35:56.086  DEBUG --- Running ARC Job Completed Hooks[0m
2026-06-23T14:35:56.0923490Z [0;37m2026-06-23 14:35:56.09  DEBUG --- Running hook: /etc/arc/hooks/job-completed.d/update-status[0m
2026-06-23T14:35:56.1168820Z Cleaning up orphan processes
2026-06-23T14:35:56.1271858Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/cache@v3, actions/setup-java@v4. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 6. `apache__beam__088751256715.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/apache__beam__088751256715.txt` (authoritative; read this, not the excerpt)
- **Repository**: `apache/beam`
- **Content hash (sha256, first 16)**: `2878c96ceaa7eb9f`
- **Body size**: 562,156 bytes, 4,316 lines
- **Excerpt**: final 120 of 4,316 lines, content-blind

```text
2026-07-21T20:49:06.8145766Z Root directory input is valid!
2026-07-21T20:49:07.0696931Z Uploading artifact: Python 3.13 Test Results Array.zip
2026-07-21T20:49:07.0774644Z Beginning upload of artifact content to blob storage
2026-07-21T20:49:07.3783063Z Uploaded bytes 14927
2026-07-21T20:49:07.4216619Z Finished uploading artifact content to blob storage!
2026-07-21T20:49:07.4217912Z SHA256 digest of uploaded artifact is 3db037b3b14e82e6938de4368075cab71ee73502aef1ae751f5d64a8aa4bb20a
2026-07-21T20:49:07.4219007Z Finalizing artifact upload
2026-07-21T20:49:07.7258960Z Artifact Python 3.13 Test Results Array successfully finalized. Artifact ID 8509733625
2026-07-21T20:49:07.7260879Z Artifact Python 3.13 Test Results Array has been successfully uploaded! Final size is 14927 bytes. Artifact ID is 8509733625
2026-07-21T20:49:07.7268543Z Artifact download URL: https://github.com/apache/beam/actions/runs/29865114858/artifacts/8509733625
2026-07-21T20:49:07.9514079Z ##[group]Run EnricoMi/publish-unit-test-result-action@v2
2026-07-21T20:49:07.9514568Z with:
2026-07-21T20:49:07.9514837Z   comment_mode: off
2026-07-21T20:49:07.9515109Z   files: **/pytest*.xml
2026-07-21T20:49:07.9515389Z   large_files: true
2026-07-21T20:49:07.9515843Z   check_name: Python 3.13 Test Results (self-hosted, ubuntu-24.04, main)
2026-07-21T20:49:07.9518953Z   github_token: ***
2026-07-21T20:49:07.9519250Z   github_retries: 10
2026-07-21T20:49:07.9519534Z   ssl_verify: true
2026-07-21T20:49:07.9519803Z   fail_on: test failures
2026-07-21T20:49:07.9520094Z   action_fail: false
2026-07-21T20:49:07.9520390Z   action_fail_on_inconclusive: false
2026-07-21T20:49:07.9520751Z   time_unit: seconds
2026-07-21T20:49:07.9521040Z   report_suite_logs: none
2026-07-21T20:49:07.9521334Z   ignore_runs: false
2026-07-21T20:49:07.9521604Z   check_run: true
2026-07-21T20:49:07.9521916Z   job_summary: true
2026-07-21T20:49:07.9522554Z   compare_to_earlier_commit: true
2026-07-21T20:49:07.9523145Z   pull_request_build: merge
2026-07-21T20:49:07.9523511Z   check_run_annotations: all tests, skipped tests
2026-07-21T20:49:07.9523901Z   seconds_between_github_reads: 0.25
2026-07-21T20:49:07.9524253Z   seconds_between_github_writes: 2.0
2026-07-21T20:49:07.9524589Z   json_thousands_separator:  
2026-07-21T20:49:07.9524918Z   json_suite_details: false
2026-07-21T20:49:07.9525222Z   json_test_case_results: false
2026-07-21T20:49:07.9525544Z   search_pull_requests: false
2026-07-21T20:49:07.9525853Z env:
2026-07-21T20:49:07.9526105Z   DEVELOCITY_ACCESS_KEY: 
2026-07-21T20:49:07.9526455Z   GRADLE_ENTERPRISE_CACHE_USERNAME: ***
2026-07-21T20:49:07.9527228Z   GRADLE_ENTERPRISE_CACHE_PASSWORD: ***
2026-07-21T20:49:07.9527604Z   ALLOYDB_PASSWORD: ***
2026-07-21T20:49:07.9528235Z   KUBELET_GCLOUD_CONFIG_PATH: /var/lib/kubelet/pods/d4417a83-339e-4307-a6d3-cc1d0c84bc8d/volumes/kubernetes.io~empty-dir/gcloud
2026-07-21T20:49:07.9528960Z   pythonLocation: /opt/hostedtoolcache/Python/3.13.14/x64
2026-07-21T20:49:07.9529492Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.13.14/x64/lib/pkgconfig
2026-07-21T20:49:07.9530004Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.13.14/x64
2026-07-21T20:49:07.9530451Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.13.14/x64
2026-07-21T20:49:07.9530904Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.13.14/x64
2026-07-21T20:49:07.9531363Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.13.14/x64/lib
2026-07-21T20:49:07.9531888Z   JAVA_HOME: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/21.0.11-10.0.LTS/x64
2026-07-21T20:49:07.9532756Z   JAVA_HOME_21_X64: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/21.0.11-10.0.LTS/x64
2026-07-21T20:49:07.9533255Z   MAVEN_ARGS: -ntp
2026-07-21T20:49:07.9533571Z   GRADLE_ACTION_ID: gradle/actions/setup-gradle
2026-07-21T20:49:07.9533945Z   GRADLE_USER_HOME: /home/runner/.gradle
2026-07-21T20:49:07.9534295Z   GRADLE_BUILD_ACTION_SETUP_COMPLETED: true
2026-07-21T20:49:07.9534819Z   DEVELOCITY_INJECTION_INIT_SCRIPT_NAME: gradle-actions.inject-develocity.init.gradle
2026-07-21T20:49:07.9535363Z   DEVELOCITY_INJECTION_CUSTOM_VALUE: gradle-actions
2026-07-21T20:49:07.9535746Z   GITHUB_DEPENDENCY_GRAPH_ENABLED: false
2026-07-21T20:49:07.9536091Z ##[endgroup]
2026-07-21T20:49:07.9978199Z ##[command]/usr/local/bin/docker run --name ghcrioenricomipublishunittestresultactionv2240_bca6e0 --label 3a9689 --workdir /github/workspace --rm -e "DEVELOCITY_ACCESS_KEY" -e "GRADLE_ENTERPRISE_CACHE_USERNAME" -e "GRADLE_ENTERPRISE_CACHE_PASSWORD" -e "ALLOYDB_PASSWORD" -e "KUBELET_GCLOUD_CONFIG_PATH" -e "pythonLocation" -e "PKG_CONFIG_PATH" -e "Python_ROOT_DIR" -e "Python2_ROOT_DIR" -e "Python3_ROOT_DIR" -e "LD_LIBRARY_PATH" -e "JAVA_HOME" -e "JAVA_HOME_21_X64" -e "MAVEN_ARGS" -e "GRADLE_ACTION_ID" -e "GRADLE_USER_HOME" -e "GRADLE_BUILD_ACTION_SETUP_COMPLETED" -e "DEVELOCITY_INJECTION_INIT_SCRIPT_NAME" -e "DEVELOCITY_INJECTION_CUSTOM_VALUE" -e "GITHUB_DEPENDENCY_GRAPH_ENABLED" -e "INPUT_COMMIT" -e "INPUT_COMMENT_MODE" -e "INPUT_FILES" -e "INPUT_LARGE_FILES" -e "INPUT_CHECK_NAME" -e "INPUT_GITHUB_TOKEN" -e "INPUT_GITHUB_TOKEN_ACTOR" -e "INPUT_GITHUB_RETRIES" -e "INPUT_SSL_VERIFY" -e "INPUT_COMMENT_TITLE" -e "INPUT_FAIL_ON" -e "INPUT_ACTION_FAIL" -e "INPUT_ACTION_FAIL_ON_INCONCLUSIVE" -e "INPUT_JUNIT_FILES" -e "INPUT_NUNIT_FILES" -e "INPUT_XUNIT_FILES" -e "INPUT_TRX_FILES" -e "INPUT_TIME_UNIT" -e "INPUT_TEST_FILE_PREFIX" -e "INPUT_REPORT_INDIVIDUAL_RUNS" -e "INPUT_REPORT_SUITE_LOGS" -e "INPUT_DEDUPLICATE_CLASSES_BY_FILE_NAME" -e "INPUT_IGNORE_RUNS" -e "INPUT_CHECK_RUN" -e "INPUT_JOB_SUMMARY" -e "INPUT_COMPARE_TO_EARLIER_COMMIT" -e "INPUT_PULL_REQUEST_BUILD" -e "INPUT_EVENT_FILE" -e "INPUT_EVENT_NAME" -e "INPUT_TEST_CHANGES_LIMIT" -e "INPUT_CHECK_RUN_ANNOTATIONS" -e "INPUT_CHECK_RUN_ANNOTATIONS_BRANCH" -e "INPUT_SECONDS_BETWEEN_GITHUB_READS" -e "INPUT_SECONDS_BETWEEN_GITHUB_WRITES" -e "INPUT_SECONDARY_RATE_LIMIT_WAIT_SECONDS" -e "INPUT_JSON_FILE" -e "INPUT_JSON_THOUSANDS_SEPARATOR" -e "INPUT_JSON_SUITE_DETAILS" -e "INPUT_JSON_TEST_CASE_RESULTS" -e "INPUT_SEARCH_PULL_REQUESTS" -e "HOME" -e "GITHUB_JOB" -e "GITHUB_REF" -e "GITHUB_SHA" -e "GITHUB_REPOSITORY" -e "GITHUB_REPOSITORY_OWNER" -e "GITHUB_REPOSITORY_OWNER_ID" -e "GITHUB_RUN_ID" -e "GITHUB_RUN_NUMBER" -e "GITHUB_RETENTION_DAYS" -e "GITHUB_RUN_ATTEMPT" -e "GITHUB_ACTOR_ID" -e "GITHUB_ACTOR" -e "GITHUB_WORKFLOW" -e "GITHUB_HEAD_REF" -e "GITHUB_BASE_REF" -e "GITHUB_EVENT_NAME" -e "GITHUB_SERVER_URL" -e "GITHUB_API_URL" -e "GITHUB_GRAPHQL_URL" -e "GITHUB_REF_NAME" -e "GITHUB_REF_PROTECTED" -e "GITHUB_REF_TYPE" -e "GITHUB_WORKFLOW_REF" -e "GITHUB_WORKFLOW_SHA" -e "GITHUB_REPOSITORY_ID" -e "GITHUB_TRIGGERING_ACTOR" -e "GITHUB_WORKSPACE" -e "GITHUB_EVENT_PATH" -e "GITHUB_PATH" -e "GITHUB_ENV" -e "GITHUB_STEP_SUMMARY" -e "GITHUB_STATE" -e "GITHUB_OUTPUT" -e "GITHUB_ACTION" -e "GITHUB_ACTION_REPOSITORY" -e "GITHUB_ACTION_REF" -e "RUNNER_OS" -e "RUNNER_ARCH" -e "RUNNER_NAME" -e "RUNNER_ENVIRONMENT" -e "RUNNER_TOOL_CACHE" -e "RUNNER_TEMP" -e "RUNNER_WORKSPACE" -e "ACTIONS_RUNTIME_URL" -e "ACTIONS_RUNTIME_TOKEN" -e "ACTIONS_CACHE_URL" -e "ACTIONS_RESULTS_URL" -e "ACTIONS_ORCHESTRATION_ID" -e GITHUB_ACTIONS=true -e CI=true -v "/var/run/docker.sock":"/var/run/docker.sock" -v "/runner/_work/_temp":"/github/runner_temp" -v "/runner/_work/_temp/_github_home":"/github/home" -v "/runner/_work/_temp/_github_workflow":"/github/workflow" -v "/runner/_work/_temp/_runner_file_commands":"/github/file_commands" -v "/runner/_work/beam/beam":"/github/workspace" ghcr.io/enricomi/publish-unit-test-result-action:v2.24.0
2026-07-21T20:49:13.7956262Z 2026-07-21 20:49:13 +0000 - publish -  INFO - Available memory to read files: 34.4 GiB
2026-07-21T20:49:14.1654283Z 2026-07-21 20:49:14 +0000 - publish -  INFO - Reading files **/pytest*.xml (2 files, 139.5 KiB)
2026-07-21T20:49:14.1748095Z 2026-07-21 20:49:14 +0000 - publish -  INFO - Detected 2 JUnit XML files (139.5 KiB)
2026-07-21T20:49:14.1749220Z 2026-07-21 20:49:14 +0000 - publish -  INFO - Finished reading 2 files in 0.01 seconds
2026-07-21T20:49:14.5366960Z 2026-07-21 20:49:14 +0000 - publish -  INFO - Publishing failure results for commit 058a4d7003404f5923f6dbd4bd456d1e5ad8cbce
2026-07-21T20:49:15.2083030Z 2026-07-21 20:49:15 +0000 - publish -  INFO - Created check https://github.com/apache/beam/runs/88758913298
2026-07-21T20:49:15.2102968Z 2026-07-21 20:49:15 +0000 - publish -  INFO - Created job summary
2026-07-21T20:49:15.2104202Z 2026-07-21 20:49:15 +0000 - publish -  INFO - Commenting on pull requests disabled
2026-07-21T20:49:22.2874364Z Post job cleanup.
2026-07-21T20:49:22.3285219Z Post job cleanup.
2026-07-21T20:49:22.7703280Z In post-action step
2026-07-21T20:49:22.7714628Z Enhanced Caching: This build is using the proprietary 'gradle-actions-caching' provider for optimized caching support. See https://github.com/gradle/actions/blob/main/DISTRIBUTION.md for terms of use and opt-out instructions.
2026-07-21T20:49:22.8970802Z ##[group]Stopping Gradle daemons
2026-07-21T20:49:22.8972815Z Stopping Gradle daemons for /home/runner/.gradle/wrapper/dists/gradle-8.14.3-bin/cv11ve7ro1n3o1j4so8xd9n66/gradle-8.14.3
2026-07-21T20:49:22.8991774Z [command]/home/runner/.gradle/wrapper/dists/gradle-8.14.3-bin/cv11ve7ro1n3o1j4so8xd9n66/gradle-8.14.3/bin/gradle --stop
2026-07-21T20:49:24.8212155Z No Gradle daemons are running.
2026-07-21T20:49:24.8820835Z ##[endgroup]
2026-07-21T20:49:24.8821768Z Not performing cache-cleanup due to build failure
2026-07-21T20:49:24.8823127Z ##[group]Caching Gradle state
2026-07-21T20:49:25.2305534Z [command]/usr/bin/tar --posix -cf cache.tgz --exclude cache.tgz -P -C /runner/_work/beam/beam --files-from manifest.txt -z
2026-07-21T20:49:25.4176728Z [command]/usr/bin/tar --posix -cf cache.tgz --exclude cache.tgz -P -C /runner/_work/beam/beam --files-from manifest.txt -z
2026-07-21T20:49:25.5361143Z ##[warning]Cache reservation failed: cache write denied: token has no writable scopes
2026-07-21T20:49:25.5366256Z Failed to save cache entry with path '/home/runner/.gradle/caches/jars-*/*/' and key: gradle-instrumented-jars-v1-39fd0d96d62acd8219495262204b2e13: ReserveCacheError: Unable to reserve cache with key gradle-instrumented-jars-v1-39fd0d96d62acd8219495262204b2e13, another job may be creating this cache.
2026-07-21T20:49:25.6331840Z [command]/usr/bin/tar --posix -cf cache.tgz --exclude cache.tgz -P -C /runner/_work/beam/beam --files-from manifest.txt -z
2026-07-21T20:49:25.8862174Z ##[warning]Cache reservation failed: cache write denied: token has no writable scopes
2026-07-21T20:49:25.8869774Z Failed to save cache entry with path '/home/runner/.gradle/caches/*/groovy-dsl/*/' and key: gradle-groovy-dsl-v1-60e652c677e08eca8fedb1cdd487159c: ReserveCacheError: Unable to reserve cache with key gradle-groovy-dsl-v1-60e652c677e08eca8fedb1cdd487159c, another job may be creating this cache.
2026-07-21T20:49:26.2711557Z [command]/usr/bin/tar --posix -cf cache.tgz --exclude cache.tgz -P -C /runner/_work/beam/beam --files-from manifest.txt -z
2026-07-21T20:49:32.2260104Z ##[warning]Cache reservation failed: cache write denied: token has no writable scopes
2026-07-21T20:49:32.2416715Z Failed to save cache entry with path '/home/runner/.gradle/caches/modules-*/files-*/*/*/*/*' and key: gradle-dependencies-v1-672084b6421f11227e7e25dbc42886a7: ReserveCacheError: Unable to reserve cache with key gradle-dependencies-v1-672084b6421f11227e7e25dbc42886a7, another job may be creating this cache.
2026-07-21T20:49:39.0131504Z ##[warning]Cache reservation failed: cache write denied: token has no writable scopes
2026-07-21T20:49:39.0258773Z Failed to save cache entry with path '/home/runner/.gradle/caches/transforms-4/*/,/home/runner/.gradle/caches/*/transforms/*/' and key: gradle-transforms-v1-89bcbe49c736c360cd4dfeb4bfcca4fb: ReserveCacheError: Unable to reserve cache with key gradle-transforms-v1-89bcbe49c736c360cd4dfeb4bfcca4fb, another job may be creating this cache.
2026-07-21T20:49:39.3095179Z [command]/usr/bin/tar --posix -cf cache.tgz --exclude cache.tgz -P -C /runner/_work/beam/beam --files-from manifest.txt -z
2026-07-21T20:50:06.7585088Z ##[warning]Cache reservation failed: cache write denied: token has no writable scopes
2026-07-21T20:50:06.8107732Z Failed to save cache entry with path '/home/runner/.gradle/caches,/home/runner/.gradle/notifications,/home/runner/.gradle/.setup-gradle' and key: gradle-home-v1|Linux-X64|beam_PreCommit_Python_ML[9bd0790bef6911831b2e18eedc9dfea0]-55e1ecbb138ccf8a8ce423f68b618db22bc0b23d: ReserveCacheError: Unable to reserve cache with key gradle-home-v1|Linux-X64|beam_PreCommit_Python_ML[9bd0790bef6911831b2e18eedc9dfea0]-55e1ecbb138ccf8a8ce423f68b618db22bc0b23d, another job may be creating this cache.
2026-07-21T20:50:06.8113962Z ##[endgroup]
2026-07-21T20:50:06.8126020Z Generating Job Summary
2026-07-21T20:50:06.8158270Z Completed post-action step
2026-07-21T20:50:06.8622826Z Post job cleanup.
2026-07-21T20:50:07.1274842Z Post job cleanup.
2026-07-21T20:50:07.1494964Z Post job cleanup.
2026-07-21T20:50:07.3313789Z [command]/usr/bin/git version
2026-07-21T20:50:07.3386651Z git version 2.54.0
2026-07-21T20:50:07.3469081Z Temporarily overriding HOME='/runner/_work/_temp/a825f0df-42f8-4a7b-ba9e-e4822cad1ae0' before making global git config changes
2026-07-21T20:50:07.3470860Z Adding repository directory to the temporary git global config as a safe directory
2026-07-21T20:50:07.3493702Z [command]/usr/bin/git config --global --add safe.directory /runner/_work/beam/beam
2026-07-21T20:50:07.3557903Z Removing SSH command configuration
2026-07-21T20:50:07.3571523Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-07-21T20:50:07.3638644Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-07-21T20:50:07.4179118Z Removing HTTP extra header
2026-07-21T20:50:07.4194033Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-21T20:50:07.4276783Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-07-21T20:50:07.4865397Z Removing includeIf entries pointing to credentials config files
2026-07-21T20:50:07.4868470Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-21T20:50:07.4931489Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-07-21T20:50:07.5695389Z A job completed hook has been configured by the self-hosted runner administrator
2026-07-21T20:50:07.5735036Z ##[group]Run '/etc/arc/hooks/job-completed.sh'
2026-07-21T20:50:07.5754168Z shell: /usr/bin/bash --noprofile --norc -e -o pipefail {0}
2026-07-21T20:50:07.5754936Z ##[endgroup]
2026-07-21T20:50:07.5856028Z [0;37m2026-07-21 20:50:07.584  DEBUG --- Running ARC Job Completed Hooks[0m
2026-07-21T20:50:07.5887696Z [0;37m2026-07-21 20:50:07.587  DEBUG --- Running hook: /etc/arc/hooks/job-completed.d/update-status[0m
2026-07-21T20:50:07.6088990Z Cleaning up orphan processes
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 7. `apache__flink__080018153058.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/apache__flink__080018153058.txt` (authoritative; read this, not the excerpt)
- **Repository**: `apache/flink`
- **Content hash (sha256, first 16)**: `621a2725b34505f6`
- **Body size**: 1,499,173 bytes, 11,570 lines
- **Excerpt**: final 120 of 11,570 lines, content-blind

```text
2026-06-08T03:39:45.2705774Z Jun 08 03:39:45 03:39:45.263 [ERROR] After correcting the problems, you can resume the build with the command
2026-06-08T03:39:45.2706796Z Jun 08 03:39:45 03:39:45.263 [ERROR]   mvn <args> -rf :flink-runtime
2026-06-08T03:39:45.6105309Z Jun 08 03:39:45 Process exited with EXIT CODE: 1.
2026-06-08T03:39:45.6105811Z Jun 08 03:39:45 Trying to KILL watchdog (794).
2026-06-08T03:39:45.6170876Z Jun 08 03:39:45 Searching for .dump, .dumpstream and related files in '/root/flink'
2026-06-08T03:39:54.3119341Z ##[error]Process completed with exit code 1.
2026-06-08T03:39:54.3168291Z ##[group]Run df -h
2026-06-08T03:39:54.3168554Z [36;1mdf -h[0m
2026-06-08T03:39:54.3168926Z shell: bash --noprofile --norc -e -o pipefail {0}
2026-06-08T03:39:54.3169240Z env:
2026-06-08T03:39:54.3169454Z   MOUNTED_WORKING_DIR: /__w/flink/flink
2026-06-08T03:39:54.3169754Z   CONTAINER_LOCAL_WORKING_DIR: /root/flink
2026-06-08T03:39:54.3170290Z   FLINK_ARTIFACT_DIR: /root/artifact-directory
2026-06-08T03:39:54.3170665Z   FLINK_ARTIFACT_FILENAME: flink_artifacts.tar.gz
2026-06-08T03:39:54.3170993Z   MAVEN_REPO_FOLDER: /root/.m2/repository
2026-06-08T03:39:54.3171327Z   MAVEN_ARGS: -Dmaven.repo.local=/root/.m2/repository
2026-06-08T03:39:54.3171677Z   DOCKER_IMAGES_CACHE_FOLDER: /root/.docker-cache
2026-06-08T03:39:54.3171981Z   GHA_JOB_TIMEOUT: 240
2026-06-08T03:39:54.3172253Z   GHA_PIPELINE_START_TIME: 2026-06-08 03:29:18+00:00
2026-06-08T03:39:54.3172568Z   JAVA_HOME: /usr/lib/jvm/jdk-21.0.1+12
2026-06-08T03:39:54.3173058Z   PATH: /usr/lib/jvm/jdk-21.0.1+12/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
2026-06-08T03:39:54.3173517Z ##[endgroup]
2026-06-08T03:39:54.3625606Z Filesystem      Size  Used Avail Use% Mounted on
2026-06-08T03:39:54.3626520Z overlay         145G   62G   83G  43% /
2026-06-08T03:39:54.3627477Z tmpfs            64M     0   64M   0% /dev
2026-06-08T03:39:54.3628173Z shm              64M     0   64M   0% /dev/shm
2026-06-08T03:39:54.3632249Z /dev/root       145G   62G   83G  43% /root
2026-06-08T03:39:54.3632981Z tmpfs           3.2G  1.2M  3.2G   1% /run/docker.sock
2026-06-08T03:39:54.3683995Z ##[group]Run du -ah --exclude="proc" -t100M . | sort -h -r | head -n 15
2026-06-08T03:39:54.3684497Z [36;1mdu -ah --exclude="proc" -t100M . | sort -h -r | head -n 15[0m
2026-06-08T03:39:54.3685005Z shell: bash --noprofile --norc -e -o pipefail {0}
2026-06-08T03:39:54.3685311Z env:
2026-06-08T03:39:54.3685527Z   MOUNTED_WORKING_DIR: /__w/flink/flink
2026-06-08T03:39:54.3685830Z   CONTAINER_LOCAL_WORKING_DIR: /root/flink
2026-06-08T03:39:54.3686142Z   FLINK_ARTIFACT_DIR: /root/artifact-directory
2026-06-08T03:39:54.3686661Z   FLINK_ARTIFACT_FILENAME: flink_artifacts.tar.gz
2026-06-08T03:39:54.3686991Z   MAVEN_REPO_FOLDER: /root/.m2/repository
2026-06-08T03:39:54.3687319Z   MAVEN_ARGS: -Dmaven.repo.local=/root/.m2/repository
2026-06-08T03:39:54.3687666Z   DOCKER_IMAGES_CACHE_FOLDER: /root/.docker-cache
2026-06-08T03:39:54.3687964Z   GHA_JOB_TIMEOUT: 240
2026-06-08T03:39:54.3688233Z   GHA_PIPELINE_START_TIME: 2026-06-08 03:29:18+00:00
2026-06-08T03:39:54.3688608Z   JAVA_HOME: /usr/lib/jvm/jdk-21.0.1+12
2026-06-08T03:39:54.3689059Z   PATH: /usr/lib/jvm/jdk-21.0.1+12/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
2026-06-08T03:39:54.3689496Z ##[endgroup]
2026-06-08T03:39:54.4283571Z ##[group]Run actions/upload-artifact@v5
2026-06-08T03:39:54.4284037Z with:
2026-06-08T03:39:54.4284514Z   name: logs-test-nightly-beta-java21-3479-core-test-1780889395
2026-06-08T03:39:54.4285109Z   path: /__w/_temp/debug_files
2026-06-08T03:39:54.4285428Z   if-no-files-found: warn
2026-06-08T03:39:54.4285704Z   compression-level: 6
2026-06-08T03:39:54.4285942Z   overwrite: false
2026-06-08T03:39:54.4286180Z   include-hidden-files: false
2026-06-08T03:39:54.4286433Z env:
2026-06-08T03:39:54.4286782Z   MOUNTED_WORKING_DIR: /__w/flink/flink
2026-06-08T03:39:54.4287235Z   CONTAINER_LOCAL_WORKING_DIR: /root/flink
2026-06-08T03:39:54.4287563Z   FLINK_ARTIFACT_DIR: /root/artifact-directory
2026-06-08T03:39:54.4287972Z   FLINK_ARTIFACT_FILENAME: flink_artifacts.tar.gz
2026-06-08T03:39:54.4288483Z   MAVEN_REPO_FOLDER: /root/.m2/repository
2026-06-08T03:39:54.4289007Z   MAVEN_ARGS: -Dmaven.repo.local=/root/.m2/repository
2026-06-08T03:39:54.4289608Z   DOCKER_IMAGES_CACHE_FOLDER: /root/.docker-cache
2026-06-08T03:39:54.4290339Z   GHA_JOB_TIMEOUT: 240
2026-06-08T03:39:54.4290761Z   GHA_PIPELINE_START_TIME: 2026-06-08 03:29:18+00:00
2026-06-08T03:39:54.4291270Z   JAVA_HOME: /usr/lib/jvm/jdk-21.0.1+12
2026-06-08T03:39:54.4291979Z   PATH: /usr/lib/jvm/jdk-21.0.1+12/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
2026-06-08T03:39:54.4292615Z ##[endgroup]
2026-06-08T03:39:54.4297574Z ##[command]/usr/bin/docker exec  a75f42d39d1790ebba56c1d96b6d18a825042994f337afd6f35e7914389a6481 sh -c "cat /etc/*release | grep ^ID"
2026-06-08T03:39:54.7320801Z With the provided path, there will be 12 files uploaded
2026-06-08T03:39:54.7323731Z Artifact name is valid!
2026-06-08T03:39:54.7326024Z Root directory input is valid!
2026-06-08T03:39:54.8512089Z Beginning upload of artifact content to blob storage
2026-06-08T03:39:56.3983967Z Uploaded bytes 6475711
2026-06-08T03:39:56.4174905Z Finished uploading artifact content to blob storage!
2026-06-08T03:39:56.4177721Z SHA256 digest of uploaded artifact zip is 36b4cb29ebf69aa0bb673484ee146f23d786b13ce9ae14c40990db45eb617aac
2026-06-08T03:39:56.4180289Z Finalizing artifact upload
2026-06-08T03:39:56.5346245Z Artifact logs-test-nightly-beta-java21-3479-core-test-1780889395.zip successfully finalized. Artifact ID 7471190054
2026-06-08T03:39:56.5347877Z Artifact logs-test-nightly-beta-java21-3479-core-test-1780889395 has been successfully uploaded! Final size is 6475711 bytes. Artifact ID is 7471190054
2026-06-08T03:39:56.5354921Z Artifact download URL: https://github.com/apache/flink/actions/runs/27113488102/artifacts/7471190054
2026-06-08T03:39:56.5509094Z ##[group]Run ./tools/azure-pipelines/cache_docker_images.sh save
2026-06-08T03:39:56.5509590Z [36;1m./tools/azure-pipelines/cache_docker_images.sh save[0m
2026-06-08T03:39:56.5510015Z shell: sh -e {0}
2026-06-08T03:39:56.5510613Z env:
2026-06-08T03:39:56.5510835Z   MOUNTED_WORKING_DIR: /__w/flink/flink
2026-06-08T03:39:56.5511143Z   CONTAINER_LOCAL_WORKING_DIR: /root/flink
2026-06-08T03:39:56.5511461Z   FLINK_ARTIFACT_DIR: /root/artifact-directory
2026-06-08T03:39:56.5511809Z   FLINK_ARTIFACT_FILENAME: flink_artifacts.tar.gz
2026-06-08T03:39:56.5512139Z   MAVEN_REPO_FOLDER: /root/.m2/repository
2026-06-08T03:39:56.5512473Z   MAVEN_ARGS: -Dmaven.repo.local=/root/.m2/repository
2026-06-08T03:39:56.5512821Z   DOCKER_IMAGES_CACHE_FOLDER: /root/.docker-cache
2026-06-08T03:39:56.5513343Z   GHA_JOB_TIMEOUT: 240
2026-06-08T03:39:56.5513612Z   GHA_PIPELINE_START_TIME: 2026-06-08 03:29:18+00:00
2026-06-08T03:39:56.5513933Z   JAVA_HOME: /usr/lib/jvm/jdk-21.0.1+12
2026-06-08T03:39:56.5514425Z   PATH: /usr/lib/jvm/jdk-21.0.1+12/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
2026-06-08T03:39:56.5514887Z ##[endgroup]
2026-06-08T03:39:56.5925432Z ==============================================================================
2026-06-08T03:39:56.5925997Z Saving Docker Images
2026-06-08T03:39:56.5926311Z ==============================================================================
2026-06-08T03:39:56.5926568Z 
2026-06-08T03:39:56.6422374Z No images found that match pattern (testcontainers|kafka|mysql|pulsar|schema-registry). Skipping.
2026-06-08T03:39:56.6543521Z Post job cleanup.
2026-06-08T03:39:56.6609055Z Post job cleanup.
2026-06-08T03:39:56.6617292Z ##[command]/usr/bin/docker exec  a75f42d39d1790ebba56c1d96b6d18a825042994f337afd6f35e7914389a6481 sh -c "cat /etc/*release | grep ^ID"
2026-06-08T03:39:56.8114860Z [command]/usr/bin/git version
2026-06-08T03:39:56.8169775Z git version 2.47.1
2026-06-08T03:39:56.8210319Z Temporarily overriding HOME='/__w/_temp/3e4aa268-4927-4bdf-a665-c28fbe63fd38' before making global git config changes
2026-06-08T03:39:56.8211495Z Adding repository directory to the temporary git global config as a safe directory
2026-06-08T03:39:56.8215058Z [command]/usr/bin/git config --global --add safe.directory /__w/flink/flink
2026-06-08T03:39:56.8271395Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-06-08T03:39:56.8318410Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-06-08T03:39:56.8858910Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-06-08T03:39:56.8915357Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-06-08T03:39:56.9421042Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-06-08T03:39:56.9465927Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-06-08T03:39:57.0085238Z Stop and remove container: d69f526d2d0144108853615c8c813429_chesnayflinkcijava_8_11_17_21_maven_386_jammy_fa833c
2026-06-08T03:39:57.0090406Z ##[command]/usr/bin/docker rm --force a75f42d39d1790ebba56c1d96b6d18a825042994f337afd6f35e7914389a6481
2026-06-08T03:39:57.1985808Z a75f42d39d1790ebba56c1d96b6d18a825042994f337afd6f35e7914389a6481
2026-06-08T03:39:57.2016305Z Remove container network: github_network_48089951847740a081cb6a9690a201e7
2026-06-08T03:39:57.2020919Z ##[command]/usr/bin/docker network rm github_network_48089951847740a081cb6a9690a201e7
2026-06-08T03:39:57.2905840Z github_network_48089951847740a081cb6a9690a201e7
2026-06-08T03:39:57.2970710Z Cleaning up orphan processes
2026-06-08T03:39:57.3326870Z ##[warning]Node.js 20 actions are deprecated. The following actions are running on Node.js 20 and may not work as expected: actions/download-artifact@v5, actions/upload-artifact@v5. Actions will be forced to run with Node.js 24 by default starting June 16th, 2026. Node.js 20 will be removed from the runner on September 16th, 2026. Please check if updated versions of these actions are available that support Node.js 24. To opt into Node.js 24 now, set the FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true environment variable on the runner or in your workflow file. Once Node.js 24 becomes the default, you can temporarily opt out by setting ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 8. `apache__flink__080107589164.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/apache__flink__080107589164.txt` (authoritative; read this, not the excerpt)
- **Repository**: `apache/flink`
- **Content hash (sha256, first 16)**: `7a09d1d6354aa713`
- **Body size**: 2,197,132 bytes, 18,342 lines
- **Excerpt**: final 120 of 18,342 lines, content-blind

```text
2026-06-08T13:57:10.4405362Z   Python2_ROOT_DIR: /__t/Python/3.12.13/x64
2026-06-08T13:57:10.4405662Z   Python3_ROOT_DIR: /__t/Python/3.12.13/x64
2026-06-08T13:57:10.4405971Z   LD_LIBRARY_PATH: /__t/Python/3.12.13/x64/lib
2026-06-08T13:57:10.4406266Z ##[endgroup]
2026-06-08T13:57:10.4858131Z Filesystem      Size  Used Avail Use% Mounted on
2026-06-08T13:57:10.4858727Z overlay         145G   68G   77G  47% /
2026-06-08T13:57:10.4859184Z tmpfs            64M     0   64M   0% /dev
2026-06-08T13:57:10.4859828Z shm              64M     0   64M   0% /dev/shm
2026-06-08T13:57:10.4860302Z /dev/root       145G   68G   77G  47% /root
2026-06-08T13:57:10.4860809Z tmpfs           3.2G  1.2M  3.2G   1% /run/docker.sock
2026-06-08T13:57:10.4914601Z ##[group]Run du -ah --exclude="proc" -t100M . | sort -h -r | head -n 15
2026-06-08T13:57:10.4915111Z [36;1mdu -ah --exclude="proc" -t100M . | sort -h -r | head -n 15[0m
2026-06-08T13:57:10.4915721Z shell: bash --noprofile --norc -e -o pipefail {0}
2026-06-08T13:57:10.4916038Z env:
2026-06-08T13:57:10.4916269Z   MOUNTED_WORKING_DIR: /__w/flink/flink
2026-06-08T13:57:10.4916578Z   CONTAINER_LOCAL_WORKING_DIR: /root/flink
2026-06-08T13:57:10.4916908Z   FLINK_ARTIFACT_DIR: /root/artifact-directory
2026-06-08T13:57:10.4917256Z   FLINK_ARTIFACT_FILENAME: flink_artifacts.tar.gz
2026-06-08T13:57:10.4917595Z   MAVEN_REPO_FOLDER: /root/.m2/repository
2026-06-08T13:57:10.4917925Z   MAVEN_ARGS: -Dmaven.repo.local=/root/.m2/repository
2026-06-08T13:57:10.4918278Z   DOCKER_IMAGES_CACHE_FOLDER: /root/.docker-cache
2026-06-08T13:57:10.4918578Z   GHA_JOB_TIMEOUT: 240
2026-06-08T13:57:10.4918858Z   GHA_PIPELINE_START_TIME: 2026-06-08 13:38:18+00:00
2026-06-08T13:57:10.4919219Z   JAVA_HOME: /usr/lib/jvm/jdk-17.0.7+7
2026-06-08T13:57:10.4919958Z   PATH: /usr/lib/jvm/jdk-17.0.7+7/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
2026-06-08T13:57:10.4920571Z   pythonLocation: /__t/Python/3.12.13/x64
2026-06-08T13:57:10.4920916Z   PKG_CONFIG_PATH: /__t/Python/3.12.13/x64/lib/pkgconfig
2026-06-08T13:57:10.4921267Z   Python_ROOT_DIR: /__t/Python/3.12.13/x64
2026-06-08T13:57:10.4921569Z   Python2_ROOT_DIR: /__t/Python/3.12.13/x64
2026-06-08T13:57:10.4921872Z   Python3_ROOT_DIR: /__t/Python/3.12.13/x64
2026-06-08T13:57:10.4922173Z   LD_LIBRARY_PATH: /__t/Python/3.12.13/x64/lib
2026-06-08T13:57:10.4922591Z ##[endgroup]
2026-06-08T13:57:10.5520405Z ##[group]Run actions/upload-artifact@v5
2026-06-08T13:57:10.5520745Z with:
2026-06-08T13:57:10.5521045Z   name: logs-test-flink-ci-beta-3537-python-test-1780925939
2026-06-08T13:57:10.5521424Z   path: /__w/_temp/debug_files
2026-06-08T13:57:10.5521701Z   if-no-files-found: warn
2026-06-08T13:57:10.5521967Z   compression-level: 6
2026-06-08T13:57:10.5522206Z   overwrite: false
2026-06-08T13:57:10.5522444Z   include-hidden-files: false
2026-06-08T13:57:10.5522721Z env:
2026-06-08T13:57:10.5522947Z   MOUNTED_WORKING_DIR: /__w/flink/flink
2026-06-08T13:57:10.5523265Z   CONTAINER_LOCAL_WORKING_DIR: /root/flink
2026-06-08T13:57:10.5523594Z   FLINK_ARTIFACT_DIR: /root/artifact-directory
2026-06-08T13:57:10.5523940Z   FLINK_ARTIFACT_FILENAME: flink_artifacts.tar.gz
2026-06-08T13:57:10.5524286Z   MAVEN_REPO_FOLDER: /root/.m2/repository
2026-06-08T13:57:10.5524623Z   MAVEN_ARGS: -Dmaven.repo.local=/root/.m2/repository
2026-06-08T13:57:10.5525023Z   DOCKER_IMAGES_CACHE_FOLDER: /root/.docker-cache
2026-06-08T13:57:10.5525332Z   GHA_JOB_TIMEOUT: 240
2026-06-08T13:57:10.5525617Z   GHA_PIPELINE_START_TIME: 2026-06-08 13:38:18+00:00
2026-06-08T13:57:10.5525941Z   JAVA_HOME: /usr/lib/jvm/jdk-17.0.7+7
2026-06-08T13:57:10.5526398Z   PATH: /usr/lib/jvm/jdk-17.0.7+7/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
2026-06-08T13:57:10.5526859Z   pythonLocation: /__t/Python/3.12.13/x64
2026-06-08T13:57:10.5527204Z   PKG_CONFIG_PATH: /__t/Python/3.12.13/x64/lib/pkgconfig
2026-06-08T13:57:10.5527540Z   Python_ROOT_DIR: /__t/Python/3.12.13/x64
2026-06-08T13:57:10.5527843Z   Python2_ROOT_DIR: /__t/Python/3.12.13/x64
2026-06-08T13:57:10.5528148Z   Python3_ROOT_DIR: /__t/Python/3.12.13/x64
2026-06-08T13:57:10.5528469Z   LD_LIBRARY_PATH: /__t/Python/3.12.13/x64/lib
2026-06-08T13:57:10.5528763Z ##[endgroup]
2026-06-08T13:57:10.5532776Z ##[command]/usr/bin/docker exec  f7f00dc4d0a27e8d8abbf2f16c9f3093a9159467f11b93d1f9bb852aac470651 sh -c "cat /etc/*release | grep ^ID"
2026-06-08T13:57:10.8392259Z With the provided path, there will be 4 files uploaded
2026-06-08T13:57:10.8398145Z Artifact name is valid!
2026-06-08T13:57:10.8400456Z Root directory input is valid!
2026-06-08T13:57:11.0109280Z Beginning upload of artifact content to blob storage
2026-06-08T13:57:11.2969901Z Uploaded bytes 1712981
2026-06-08T13:57:11.3097403Z Finished uploading artifact content to blob storage!
2026-06-08T13:57:11.3100891Z SHA256 digest of uploaded artifact zip is 948a5af6cf000e60e69f3cb712680bb55e34a8cc61015fd340f063f508280f90
2026-06-08T13:57:11.3102591Z Finalizing artifact upload
2026-06-08T13:57:11.5517633Z Artifact logs-test-flink-ci-beta-3537-python-test-1780925939.zip successfully finalized. Artifact ID 7482351613
2026-06-08T13:57:11.5519326Z Artifact logs-test-flink-ci-beta-3537-python-test-1780925939 has been successfully uploaded! Final size is 1712981 bytes. Artifact ID is 7482351613
2026-06-08T13:57:11.5525894Z Artifact download URL: https://github.com/apache/flink/actions/runs/27139198995/artifacts/7482351613
2026-06-08T13:57:11.5665467Z ##[group]Run ./tools/azure-pipelines/cache_docker_images.sh save
2026-06-08T13:57:11.5665967Z [36;1m./tools/azure-pipelines/cache_docker_images.sh save[0m
2026-06-08T13:57:11.5666404Z shell: sh -e {0}
2026-06-08T13:57:11.5666647Z env:
2026-06-08T13:57:11.5666879Z   MOUNTED_WORKING_DIR: /__w/flink/flink
2026-06-08T13:57:11.5667196Z   CONTAINER_LOCAL_WORKING_DIR: /root/flink
2026-06-08T13:57:11.5667535Z   FLINK_ARTIFACT_DIR: /root/artifact-directory
2026-06-08T13:57:11.5667894Z   FLINK_ARTIFACT_FILENAME: flink_artifacts.tar.gz
2026-06-08T13:57:11.5668232Z   MAVEN_REPO_FOLDER: /root/.m2/repository
2026-06-08T13:57:11.5668591Z   MAVEN_ARGS: -Dmaven.repo.local=/root/.m2/repository
2026-06-08T13:57:11.5668949Z   DOCKER_IMAGES_CACHE_FOLDER: /root/.docker-cache
2026-06-08T13:57:11.5669265Z   GHA_JOB_TIMEOUT: 240
2026-06-08T13:57:11.5669557Z   GHA_PIPELINE_START_TIME: 2026-06-08 13:38:18+00:00
2026-06-08T13:57:11.5670426Z   JAVA_HOME: /usr/lib/jvm/jdk-17.0.7+7
2026-06-08T13:57:11.5671165Z   PATH: /usr/lib/jvm/jdk-17.0.7+7/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
2026-06-08T13:57:11.5671639Z   pythonLocation: /__t/Python/3.12.13/x64
2026-06-08T13:57:11.5671989Z   PKG_CONFIG_PATH: /__t/Python/3.12.13/x64/lib/pkgconfig
2026-06-08T13:57:11.5672331Z   Python_ROOT_DIR: /__t/Python/3.12.13/x64
2026-06-08T13:57:11.5672635Z   Python2_ROOT_DIR: /__t/Python/3.12.13/x64
2026-06-08T13:57:11.5672948Z   Python3_ROOT_DIR: /__t/Python/3.12.13/x64
2026-06-08T13:57:11.5673258Z   LD_LIBRARY_PATH: /__t/Python/3.12.13/x64/lib
2026-06-08T13:57:11.5673558Z ##[endgroup]
2026-06-08T13:57:11.6069160Z ==============================================================================
2026-06-08T13:57:11.6070792Z Saving Docker Images
2026-06-08T13:57:11.6071279Z ==============================================================================
2026-06-08T13:57:11.6071661Z 
2026-06-08T13:57:11.6816296Z No images found that match pattern (testcontainers|kafka|mysql|pulsar|schema-registry). Skipping.
2026-06-08T13:57:11.6946270Z Post job cleanup.
2026-06-08T13:57:11.7023537Z Post job cleanup.
2026-06-08T13:57:11.7031354Z ##[command]/usr/bin/docker exec  f7f00dc4d0a27e8d8abbf2f16c9f3093a9159467f11b93d1f9bb852aac470651 sh -c "cat /etc/*release | grep ^ID"
2026-06-08T13:57:11.8642525Z [command]/usr/bin/git version
2026-06-08T13:57:11.8697409Z git version 2.47.1
2026-06-08T13:57:11.8735879Z Temporarily overriding HOME='/__w/_temp/a265cbf8-2f61-4b3a-8cfe-b83efdeb4d35' before making global git config changes
2026-06-08T13:57:11.8736985Z Adding repository directory to the temporary git global config as a safe directory
2026-06-08T13:57:11.8741055Z [command]/usr/bin/git config --global --add safe.directory /__w/flink/flink
2026-06-08T13:57:11.8793302Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-06-08T13:57:11.8838407Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-06-08T13:57:11.9387928Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-06-08T13:57:11.9434827Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-06-08T13:57:11.9934250Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-06-08T13:57:11.9980536Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-06-08T13:57:12.0626670Z Stop and remove container: f564a693a7324d8fbbed7b714fa7f1b8_chesnayflinkcijava_8_11_17_21_maven_386_jammy_8a28ec
2026-06-08T13:57:12.0631981Z ##[command]/usr/bin/docker rm --force f7f00dc4d0a27e8d8abbf2f16c9f3093a9159467f11b93d1f9bb852aac470651
2026-06-08T13:57:12.9211435Z f7f00dc4d0a27e8d8abbf2f16c9f3093a9159467f11b93d1f9bb852aac470651
2026-06-08T13:57:12.9244016Z Remove container network: github_network_dacd31b720db4566b22ca93ebae5a5e1
2026-06-08T13:57:12.9248776Z ##[command]/usr/bin/docker network rm github_network_dacd31b720db4566b22ca93ebae5a5e1
2026-06-08T13:57:13.0495339Z github_network_dacd31b720db4566b22ca93ebae5a5e1
2026-06-08T13:57:13.0560545Z Cleaning up orphan processes
2026-06-08T13:57:13.0930476Z ##[warning]Node.js 20 actions are deprecated. The following actions are running on Node.js 20 and may not work as expected: actions/download-artifact@v5, actions/upload-artifact@v5. Actions will be forced to run with Node.js 24 by default starting June 16th, 2026. Node.js 20 will be removed from the runner on September 16th, 2026. Please check if updated versions of these actions are available that support Node.js 24. To opt into Node.js 24 now, set the FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true environment variable on the runner or in your workflow file. Once Node.js 24 becomes the default, you can temporarily opt out by setting ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 9. `apache__hertzbeat__091878341153.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/apache__hertzbeat__091878341153.txt` (authoritative; read this, not the excerpt)
- **Repository**: `apache/hertzbeat`
- **Content hash (sha256, first 16)**: `ee37d3864a1bf8d7`
- **Body size**: 5,468,158 bytes, 26,090 lines
- **Excerpt**: final 120 of 26,090 lines, content-blind

```text
2026-08-04T03:06:12.5444182Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.465848Z DEBUG hyper::proto::h1::decode: Internal log [incoming chunked header: 0x64 (100 bytes)] has been suppressed 5 times.
2026-08-04T03:06:12.5445506Z [hertzbeat-observability-e2e] [INFO] [stdout] 
2026-08-04T03:06:12.5446599Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.465854Z DEBUG hyper::proto::h1::decode: incoming chunked header: 0x64 (100 bytes)
2026-08-04T03:06:12.5447846Z [hertzbeat-observability-e2e] [INFO] [stdout] 
2026-08-04T03:06:12.5449413Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.465876Z DEBUG sink{component_kind="sink" component_id=emit_syslog component_type=opentelemetry}:request{request_id=49}:http: vector::internal_events::http_client: Internal log [HTTP response.] has been suppressed 5 times.
2026-08-04T03:06:12.5450977Z [hertzbeat-observability-e2e] [INFO] [stdout] 
2026-08-04T03:06:12.5453289Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.465889Z DEBUG sink{component_kind="sink" component_id=emit_syslog component_type=opentelemetry}:request{request_id=49}:http: vector::internal_events::http_client: HTTP response. status=404 Not Found version=HTTP/1.1 headers={"vary": "Origin", "vary": "Access-Control-Request-Method", "vary": "Access-Control-Request-Headers", "content-type": "application/json", "transfer-encoding": "chunked", "date": "Tue, 04 Aug 2026 03:06:12 GMT"} body=[unknown]
2026-08-04T03:06:12.5455576Z [hertzbeat-observability-e2e] [INFO] [stdout] 
2026-08-04T03:06:12.5456817Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.466024Z DEBUG hyper::proto::h1::conn: Internal log [incoming body completed] has been suppressed 5 times.
2026-08-04T03:06:12.5458117Z [hertzbeat-observability-e2e] [INFO] [stdout] 
2026-08-04T03:06:12.5459148Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.466036Z DEBUG hyper::proto::h1::conn: incoming body completed
2026-08-04T03:06:12.5460179Z [hertzbeat-observability-e2e] [INFO] [stdout] 
2026-08-04T03:06:12.5461511Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.466076Z DEBUG hyper::client::pool: Internal log [pooling idle connection for ("http", host.testcontainers.internal:33773)] has been suppressed 5 times.
2026-08-04T03:06:12.5462917Z [hertzbeat-observability-e2e] [INFO] [stdout] 
2026-08-04T03:06:12.5464106Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.466085Z DEBUG hyper::client::pool: pooling idle connection for ("http", host.testcontainers.internal:33773)
2026-08-04T03:06:12.5465332Z [hertzbeat-observability-e2e] [INFO] [stdout] 
2026-08-04T03:06:12.5466986Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.466101Z ERROR sink{component_kind="sink" component_id=emit_syslog component_type=opentelemetry}:request{request_id=49}: vector::sinks::util::retries: Internal log [Not retriable; dropping the request.] has been suppressed 5 times.
2026-08-04T03:06:12.5468755Z [hertzbeat-observability-e2e] [INFO] [stdout] 
2026-08-04T03:06:12.5470342Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.466105Z ERROR sink{component_kind="sink" component_id=emit_syslog component_type=opentelemetry}:request{request_id=49}: vector::sinks::util::retries: Not retriable; dropping the request. reason="Default retry strategy: Not Found"
2026-08-04T03:06:12.5471931Z [hertzbeat-observability-e2e] [INFO] [stdout] 
2026-08-04T03:06:12.5473618Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.466116Z ERROR sink{component_kind="sink" component_id=emit_syslog component_type=opentelemetry}:request{request_id=49}: vector_common::internal_event::service: Internal log [Service call failed. No retries or retries exhausted.] has been suppressed 5 times.
2026-08-04T03:06:12.5475340Z [hertzbeat-observability-e2e] [INFO] [stdout] 
2026-08-04T03:06:12.5477104Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.466120Z ERROR sink{component_kind="sink" component_id=emit_syslog component_type=opentelemetry}:request{request_id=49}: vector_common::internal_event::service: Service call failed. No retries or retries exhausted. error=None request_id=49 error_type="request_failed" stage="sending"
2026-08-04T03:06:12.5478973Z [hertzbeat-observability-e2e] [INFO] [stdout] 
2026-08-04T03:06:12.5480929Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.466136Z ERROR sink{component_kind="sink" component_id=emit_syslog component_type=opentelemetry}:request{request_id=49}: vector_common::internal_event::component_events_dropped: Internal log [Events dropped] has been suppressed 5 times.
2026-08-04T03:06:12.5482583Z [hertzbeat-observability-e2e] [INFO] [stdout] 
2026-08-04T03:06:12.5484367Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.466139Z ERROR sink{component_kind="sink" component_id=emit_syslog component_type=opentelemetry}:request{request_id=49}: vector_common::internal_event::component_events_dropped: Events dropped intentional=false count=2 reason="Service call failed. No retries or retries exhausted."
2026-08-04T03:06:12.5486454Z [hertzbeat-observability-e2e] [INFO] [stdout] 
2026-08-04T03:06:12.5487033Z [hertzbeat-observability-e2e] [ERROR] Surefire is going to kill self fork JVM. The exit has elapsed 30 seconds after System.exit(0).
2026-08-04T03:06:12.8897949Z [hertzbeat-observability-e2e] [INFO] 
2026-08-04T03:06:12.8898679Z [hertzbeat-observability-e2e] [INFO] Results:
2026-08-04T03:06:12.8901688Z [hertzbeat-observability-e2e] [INFO] 
2026-08-04T03:06:12.8902319Z [hertzbeat-observability-e2e] [ERROR] Errors: 
2026-08-04T03:06:12.8904803Z [hertzbeat-observability-e2e] [ERROR]   LogRealTimeAlertE2eTest.testRealTimeLogAlertWithGroupAlert:145 » ConditionTimeout Assertion condition Should have generated high frequency warning group alert ==> expected: <false> but was: <true> within 2 minutes.
2026-08-04T03:06:12.8916295Z [hertzbeat-observability-e2e] [ERROR]   LogRealTimeAlertE2eTest.testRealTimeLogAlertWithIndividualAlert:118 » ConditionTimeout Assertion condition Should have generated at least one alert for error logs ==> expected: <false> but was: <true> within 2 minutes.
2026-08-04T03:06:12.8920925Z [hertzbeat-observability-e2e] [ERROR]   LogIngestionE2eTest.testLogIngestion:95 » ConditionTimeout Assertion condition null within 1 minutes.
2026-08-04T03:06:12.8922235Z [hertzbeat-observability-e2e] [INFO] 
2026-08-04T03:06:12.8923226Z [hertzbeat-observability-e2e] [ERROR] Tests run: 7, Failures: 0, Errors: 3, Skipped: 0
2026-08-04T03:06:12.8924052Z [hertzbeat-observability-e2e] [INFO] 
2026-08-04T03:06:12.9036117Z [INFO] ----------------------------------------------------------------------------------------------------------------
2026-08-04T03:06:12.9045211Z [INFO] Reactor Summary for hertzbeat 2.0-SNAPSHOT:
2026-08-04T03:06:12.9046770Z [INFO] 
2026-08-04T03:06:12.9049448Z [INFO] hertzbeat .................................................................................. SUCCESS [ 10.013 s]
2026-08-04T03:06:12.9050797Z [INFO] hertzbeat-common-core ...................................................................... SUCCESS [ 32.460 s]
2026-08-04T03:06:12.9052210Z [INFO] hertzbeat-common-spring .................................................................... SUCCESS [ 25.849 s]
2026-08-04T03:06:12.9053536Z [INFO] hertzbeat-base ............................................................................. SUCCESS [  0.487 s]
2026-08-04T03:06:12.9054840Z [INFO] hertzbeat-plugin ........................................................................... SUCCESS [  2.180 s]
2026-08-04T03:06:12.9056196Z [INFO] hertzbeat-warehouse ........................................................................ SUCCESS [ 42.496 s]
2026-08-04T03:06:12.9057836Z [INFO] hertzbeat-alerter .......................................................................... SUCCESS [02:29 min]
2026-08-04T03:06:12.9059288Z [INFO] hertzbeat-remoting ......................................................................... SUCCESS [ 11.034 s]
2026-08-04T03:06:12.9060789Z [INFO] hertzbeat-collector ........................................................................ SUCCESS [  0.519 s]
2026-08-04T03:06:12.9062360Z [INFO] hertzbeat-collector-common ................................................................. SUCCESS [ 16.840 s]
2026-08-04T03:06:12.9064104Z [INFO] hertzbeat-collector-basic .................................................................. SUCCESS [ 56.090 s]
2026-08-04T03:06:12.9065716Z [INFO] hertzbeat-collector-mysql-r2dbc ............................................................ SUCCESS [01:41 min]
2026-08-04T03:06:12.9067803Z [INFO] hertzbeat-collector-kafka .................................................................. SUCCESS [  6.769 s]
2026-08-04T03:06:12.9069408Z [INFO] hertzbeat-collector-mongodb ................................................................ SUCCESS [  7.151 s]
2026-08-04T03:06:12.9070922Z [INFO] hertzbeat-collector-nebulagraph ............................................................ SUCCESS [  7.998 s]
2026-08-04T03:06:12.9072429Z [INFO] hertzbeat-collector-rocketmq ............................................................... SUCCESS [  5.718 s]
2026-08-04T03:06:12.9074063Z [INFO] hertzbeat-collector-collector .............................................................. SUCCESS [02:55 min]
2026-08-04T03:06:12.9075464Z [INFO] hertzbeat-push ............................................................................. SUCCESS [  3.759 s]
2026-08-04T03:06:12.9076837Z [INFO] hertzbeat-grafana .......................................................................... SUCCESS [  4.877 s]
2026-08-04T03:06:12.9078489Z [INFO] hertzbeat-otel ............................................................................. SUCCESS [  2.959 s]
2026-08-04T03:06:12.9079834Z [INFO] hertzbeat-observability .................................................................... SUCCESS [ 15.310 s]
2026-08-04T03:06:12.9081360Z [INFO] hertzbeat-manager .......................................................................... SUCCESS [ 27.690 s]
2026-08-04T03:06:12.9082739Z [INFO] hertzbeat-ai ............................................................................... SUCCESS [  8.906 s]
2026-08-04T03:06:12.9084083Z [INFO] hertzbeat-startup .......................................................................... SUCCESS [03:04 min]
2026-08-04T03:06:12.9085402Z [INFO] hertzbeat-e2e .............................................................................. SUCCESS [  0.362 s]
2026-08-04T03:06:12.9086906Z [INFO] hertzbeat-collector-common-e2e ............................................................. SUCCESS [  4.409 s]
2026-08-04T03:06:12.9088628Z [INFO] hertzbeat-collector-kafka-e2e .............................................................. SUCCESS [ 43.502 s]
2026-08-04T03:06:12.9090104Z [INFO] hertzbeat-collector-basic-e2e .............................................................. SUCCESS [01:37 min]
2026-08-04T03:06:12.9091608Z [INFO] hertzbeat-collector-mysql-r2dbc-e2e ........................................................ SUCCESS [01:04 min]
2026-08-04T03:06:12.9093072Z [INFO] hertzbeat-observability-e2e ................................................................ FAILURE [07:38 min]
2026-08-04T03:06:12.9094431Z [INFO] ----------------------------------------------------------------------------------------------------------------
2026-08-04T03:06:12.9095419Z [INFO] BUILD FAILURE
2026-08-04T03:06:12.9096355Z [INFO] ----------------------------------------------------------------------------------------------------------------
2026-08-04T03:06:12.9097574Z [INFO] Total time:  16:56 min (Wall Clock)
2026-08-04T03:06:12.9098340Z [INFO] Finished at: 2026-08-04T03:06:12Z
2026-08-04T03:06:12.9099306Z [INFO] ----------------------------------------------------------------------------------------------------------------
2026-08-04T03:06:12.9109527Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.2.5:test (default-test) on project hertzbeat-observability-e2e: 
2026-08-04T03:06:12.9113895Z [ERROR] 
2026-08-04T03:06:12.9115317Z [ERROR] Please refer to /home/runner/work/hertzbeat/hertzbeat/hertzbeat-e2e/hertzbeat-observability-e2e/target/surefire-reports for the individual test results.
2026-08-04T03:06:12.9117702Z [ERROR] Please refer to dump files (if any exist) [date].dump, [date]-jvmRun[N].dump and [date].dumpstream.
2026-08-04T03:06:12.9122712Z [ERROR] -> [Help 1]
2026-08-04T03:06:12.9123300Z [ERROR] 
2026-08-04T03:06:12.9124055Z [ERROR] To see the full stack trace of the errors, re-run Maven with the '-e' switch
2026-08-04T03:06:12.9125099Z [ERROR] Re-run Maven using the '-X' switch to enable verbose output
2026-08-04T03:06:12.9125902Z [ERROR] 
2026-08-04T03:06:12.9126841Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-08-04T03:06:12.9128512Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
2026-08-04T03:06:12.9129440Z [ERROR] 
2026-08-04T03:06:12.9130195Z [ERROR] After correcting the problems, you can resume the build with the command
2026-08-04T03:06:12.9131123Z [ERROR]   mvn [args] -r
2026-08-04T03:06:12.9315166Z ##[error]Process completed with exit code 1.
2026-08-04T03:06:12.9497849Z Post job cleanup.
2026-08-04T03:06:12.9503470Z ##[start-action display=Cache mvnd;id=__3c52c309-5145-48b4-8946-a9d98909004c.mvnd-cache]
2026-08-04T03:06:12.9506861Z ##[end-action id=__3c52c309-5145-48b4-8946-a9d98909004c.mvnd-cache;outcome=skipped;conclusion=skipped;duration_ms=0]
2026-08-04T03:06:12.9510091Z ##[start-action display=Set up JDK 25;id=__3c52c309-5145-48b4-8946-a9d98909004c.__actions_setup-java]
2026-08-04T03:06:12.9588434Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-08-04T03:06:12.9590346Z Post job cleanup.
2026-08-04T03:06:13.3331546Z (node:33815) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-08-04T03:06:13.3332439Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-08-04T03:06:13.3485470Z ##[end-action id=__3c52c309-5145-48b4-8946-a9d98909004c.__actions_setup-java;outcome=success;conclusion=success;duration_ms=397]
2026-08-04T03:06:13.3555396Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-08-04T03:06:13.3556669Z Post job cleanup.
2026-08-04T03:06:13.4452960Z [command]/usr/bin/git version
2026-08-04T03:06:13.4509215Z git version 2.54.0
2026-08-04T03:06:13.4549145Z Temporarily overriding HOME='/home/runner/work/_temp/ab64fb5b-7524-4562-bbbd-955f1e061636' before making global git config changes
2026-08-04T03:06:13.4551158Z Adding repository directory to the temporary git global config as a safe directory
2026-08-04T03:06:13.4563244Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/hertzbeat/hertzbeat
2026-08-04T03:06:13.4595257Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-08-04T03:06:13.4633136Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-08-04T03:06:13.4954241Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-08-04T03:06:13.4979916Z http.https://github.com/.extraheader
2026-08-04T03:06:13.4991097Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-08-04T03:06:13.5020548Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-08-04T03:06:13.5244814Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-08-04T03:06:13.5274843Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-08-04T03:06:13.5635518Z Cleaning up orphan processes
2026-08-04T03:06:13.6144541Z Terminate orphan process: pid (2315) (java)
2026-08-04T03:06:13.6587507Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/cache@v4, actions/checkout@v4, actions/setup-java@v4. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 10. `apache__hugegraph__085380370363.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/apache__hugegraph__085380370363.txt` (authoritative; read this, not the excerpt)
- **Repository**: `apache/hugegraph`
- **Content hash (sha256, first 16)**: `eb2d705b5831fe51`
- **Body size**: 1,085,084 bytes, 7,087 lines
- **Excerpt**: final 120 of 7,087 lines, content-blind

```text
2026-07-06T13:33:11.4968400Z [ERROR] testDistributedDeleteKeepsTaskResultRecoverable(org.apache.hugegraph.task.TaskAndResultSchedulerTest)  Time elapsed: 0.506 s  <<< FAILURE!
2026-07-06T13:33:11.4975110Z java.lang.AssertionError: expected:<DELETING> but was:<SUCCESS>
2026-07-06T13:33:11.4980340Z 	at org.apache.hugegraph.task.TaskAndResultSchedulerTest.testDistributedDeleteKeepsTaskResultRecoverable(TaskAndResultSchedulerTest.java:122)
2026-07-06T13:33:11.4984100Z 
2026-07-06T13:33:11.5126140Z 2026-07-06 13:33:11 [hugegraph-shutdown] [INFO] o.a.h.HugeFactory - HugeGraph is shutting down
2026-07-06T13:33:11.7034350Z 2026-07-06 13:33:11 [hugegraph-shutdown] [INFO] o.a.h.HugeFactory - HugeFactory shutdown
2026-07-06T13:33:13.1945040Z [INFO] 
2026-07-06T13:33:13.1946030Z [INFO] Results:
2026-07-06T13:33:13.1946890Z [INFO] 
2026-07-06T13:33:13.1948070Z [ERROR] Failures: 
2026-07-06T13:33:13.1952170Z [ERROR]   TaskAndResultSchedulerTest.testDistributedDeleteKeepsTaskResultRecoverable:122 expected:<DELETING> but was:<SUCCESS>
2026-07-06T13:33:13.1953400Z [INFO] 
2026-07-06T13:33:13.1955370Z [ERROR] Tests run: 781, Failures: 1, Errors: 0, Skipped: 41
2026-07-06T13:33:13.1957040Z [INFO] 
2026-07-06T13:33:13.2094930Z [INFO] ------------------------------------------------------------------------
2026-07-06T13:33:13.2095680Z [INFO] Reactor Summary for hugegraph 1.7.0:
2026-07-06T13:33:13.2096190Z [INFO] 
2026-07-06T13:33:13.2117960Z [INFO] hugegraph .......................................... SUCCESS [  4.620 s]
2026-07-06T13:33:13.2119840Z [INFO] hugegraph-commons .................................. SUCCESS [  2.954 s]
2026-07-06T13:33:13.2121040Z [INFO] hugegraph-common ................................... SUCCESS [  9.296 s]
2026-07-06T13:33:13.2122320Z [INFO] hugegraph-pd ....................................... SUCCESS [  0.690 s]
2026-07-06T13:33:13.2124470Z [INFO] hg-pd-grpc ......................................... SUCCESS [ 24.923 s]
2026-07-06T13:33:13.2125750Z [INFO] hg-pd-common ....................................... SUCCESS [  1.069 s]
2026-07-06T13:33:13.2126980Z [INFO] hg-pd-client ....................................... SUCCESS [  9.653 s]
2026-07-06T13:33:13.2128370Z [INFO] hugegraph-struct ................................... SUCCESS [  7.068 s]
2026-07-06T13:33:13.2129670Z [INFO] hugegraph-store .................................... SUCCESS [  0.274 s]
2026-07-06T13:33:13.2130970Z [INFO] hg-store-common .................................... SUCCESS [  1.505 s]
2026-07-06T13:33:13.2132280Z [INFO] hugegraph-server ................................... SUCCESS [  0.532 s]
2026-07-06T13:33:13.2133290Z [INFO] hugegraph-core ..................................... SUCCESS [ 32.920 s]
2026-07-06T13:33:13.2134180Z [INFO] hugegraph-rpc ...................................... SUCCESS [  2.143 s]
2026-07-06T13:33:13.2135320Z [INFO] hugegraph-api ...................................... SUCCESS [  5.213 s]
2026-07-06T13:33:13.2136480Z [INFO] hugegraph-cassandra ................................ SUCCESS [  3.699 s]
2026-07-06T13:33:13.2137500Z [INFO] hugegraph-scylladb ................................. SUCCESS [  4.043 s]
2026-07-06T13:33:13.2139830Z [INFO] hugegraph-rocksdb .................................. SUCCESS [  3.048 s]
2026-07-06T13:33:13.2141620Z [INFO] hugegraph-mysql .................................... SUCCESS [  3.185 s]
2026-07-06T13:33:13.2142530Z [INFO] hugegraph-palo ..................................... SUCCESS [  2.577 s]
2026-07-06T13:33:13.2143420Z [INFO] hugegraph-hbase .................................... SUCCESS [  4.234 s]
2026-07-06T13:33:13.2144410Z [INFO] hugegraph-postgresql ............................... SUCCESS [  2.221 s]
2026-07-06T13:33:13.2145510Z [INFO] hg-store-grpc ...................................... SUCCESS [ 11.758 s]
2026-07-06T13:33:13.2146400Z [INFO] hg-store-client .................................... SUCCESS [  1.513 s]
2026-07-06T13:33:13.2147360Z [INFO] hugegraph-hstore ................................... SUCCESS [  3.223 s]
2026-07-06T13:33:13.2148280Z [INFO] hugegraph-dist ..................................... SUCCESS [  4.269 s]
2026-07-06T13:33:13.2149210Z [INFO] hugegraph-test ..................................... FAILURE [11:59 min]
2026-07-06T13:33:13.2150590Z [INFO] ------------------------------------------------------------------------
2026-07-06T13:33:13.2151220Z [INFO] BUILD FAILURE
2026-07-06T13:33:13.2151760Z [INFO] ------------------------------------------------------------------------
2026-07-06T13:33:13.2152430Z [INFO] Total time:  14:27 min
2026-07-06T13:33:13.2156950Z [INFO] Finished at: 2026-07-06T13:33:13Z
2026-07-06T13:33:13.2157920Z [INFO] ------------------------------------------------------------------------
2026-07-06T13:33:13.2293760Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.20:test (core-test) on project hugegraph-test: There are test failures.
2026-07-06T13:33:13.2297050Z [ERROR] 
2026-07-06T13:33:13.2299590Z [ERROR] Please refer to /Users/runner/work/hugegraph/hugegraph/hugegraph-server/hugegraph-test/target/surefire-reports for the individual test results.
2026-07-06T13:33:13.2303070Z [ERROR] Please refer to dump files (if any exist) [date]-jvmRun[N].dump, [date].dumpstream and [date]-jvmRun[N].dumpstream.
2026-07-06T13:33:13.2306090Z [ERROR] -> [Help 1]
2026-07-06T13:33:13.2362960Z [ERROR] 
2026-07-06T13:33:13.2364110Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-07-06T13:33:13.2365710Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-07-06T13:33:13.2366890Z [ERROR] 
2026-07-06T13:33:13.2367970Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-07-06T13:33:13.2369810Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
2026-07-06T13:33:13.2370660Z [ERROR] 
2026-07-06T13:33:13.2372600Z [ERROR] After correcting the problems, you can resume the build with the command
2026-07-06T13:33:13.2383760Z [ERROR]   mvn <args> -rf :hugegraph-test
2026-07-06T13:33:13.9808590Z ##[error]Process completed with exit code 1.
2026-07-06T13:33:14.2143650Z ##[group]Run VERSION=$(mvn help:evaluate -Dexpression=project.version -q -DforceStdout)
2026-07-06T13:33:14.2146480Z [36;1mVERSION=$(mvn help:evaluate -Dexpression=project.version -q -DforceStdout)[0m
2026-07-06T13:33:14.2149400Z [36;1mSERVER_DIR=hugegraph-server/apache-hugegraph-server-$VERSION/[0m
2026-07-06T13:33:14.2151350Z [36;1mif [ -f "$SERVER_DIR/logs/hugegraph-server.log" ]; then[0m
2026-07-06T13:33:14.2153630Z [36;1m  tail -n 200 "$SERVER_DIR/logs/hugegraph-server.log"[0m
2026-07-06T13:33:14.2154930Z [36;1mfi[0m
2026-07-06T13:33:14.2437660Z shell: /bin/bash -e {0}
2026-07-06T13:33:14.2438060Z env:
2026-07-06T13:33:14.2438380Z   USE_STAGE: false
2026-07-06T13:33:14.2438900Z   TRAVIS_DIR: hugegraph-server/hugegraph-dist/src/assembly/travis
2026-07-06T13:33:14.2439550Z   REPORT_DIR: target/site/jacoco
2026-07-06T13:33:14.2439960Z   BACKEND: rocksdb
2026-07-06T13:33:14.2440300Z   JAVA_VERSION: 11
2026-07-06T13:33:14.2440640Z   SERVER_JAVA_OPTIONS: 
2026-07-06T13:33:14.2441560Z   JAVA_HOME: /Users/runner/hostedtoolcache/Java_Zulu_jdk/11.0.31-11/x64/Contents/Home
2026-07-06T13:33:14.2442760Z   JAVA_HOME_11_X64: /Users/runner/hostedtoolcache/Java_Zulu_jdk/11.0.31-11/x64/Contents/Home
2026-07-06T13:33:14.2443580Z ##[endgroup]
2026-07-06T13:33:18.6639640Z ##[group]Run VERSION=$(mvn help:evaluate -Dexpression=project.version -q -DforceStdout)
2026-07-06T13:33:18.6641130Z [36;1mVERSION=$(mvn help:evaluate -Dexpression=project.version -q -DforceStdout)[0m
2026-07-06T13:33:18.6642370Z [36;1mSERVER_DIR=hugegraph-server/apache-hugegraph-server-$VERSION/[0m
2026-07-06T13:33:18.6643260Z [36;1mif [ -f "$SERVER_DIR/bin/pid" ]; then[0m
2026-07-06T13:33:18.6643960Z [36;1m  $TRAVIS_DIR/stop-server.sh $SERVER_DIR || true[0m
2026-07-06T13:33:18.6644600Z [36;1mfi[0m
2026-07-06T13:33:18.6710390Z shell: /bin/bash -e {0}
2026-07-06T13:33:18.6710870Z env:
2026-07-06T13:33:18.6711270Z   USE_STAGE: false
2026-07-06T13:33:18.6711900Z   TRAVIS_DIR: hugegraph-server/hugegraph-dist/src/assembly/travis
2026-07-06T13:33:18.6712660Z   REPORT_DIR: target/site/jacoco
2026-07-06T13:33:18.6713520Z   BACKEND: rocksdb
2026-07-06T13:33:18.6713940Z   JAVA_VERSION: 11
2026-07-06T13:33:18.6714370Z   SERVER_JAVA_OPTIONS: 
2026-07-06T13:33:18.6715210Z   JAVA_HOME: /Users/runner/hostedtoolcache/Java_Zulu_jdk/11.0.31-11/x64/Contents/Home
2026-07-06T13:33:18.6716420Z   JAVA_HOME_11_X64: /Users/runner/hostedtoolcache/Java_Zulu_jdk/11.0.31-11/x64/Contents/Home
2026-07-06T13:33:18.6717320Z ##[endgroup]
2026-07-06T13:33:22.1386940Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-07-06T13:33:22.1389680Z Post job cleanup.
2026-07-06T13:33:22.6500760Z (node:23327) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-07-06T13:33:22.6502290Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-07-06T13:33:22.6969090Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-07-06T13:33:22.6972550Z Post job cleanup.
2026-07-06T13:33:22.9020540Z [command]/usr/local/bin/git version
2026-07-06T13:33:22.9281910Z git version 2.54.0
2026-07-06T13:33:22.9340710Z Copying '/Users/runner/.gitconfig' to '/Users/runner/work/_temp/4e05025c-7563-463f-86e9-be639b4a70ae/.gitconfig'
2026-07-06T13:33:22.9369440Z Temporarily overriding HOME='/Users/runner/work/_temp/4e05025c-7563-463f-86e9-be639b4a70ae' before making global git config changes
2026-07-06T13:33:22.9371720Z Adding repository directory to the temporary git global config as a safe directory
2026-07-06T13:33:22.9380870Z [command]/usr/local/bin/git config --global --add safe.directory /Users/runner/work/hugegraph/hugegraph
2026-07-06T13:33:22.9611970Z [command]/usr/local/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-07-06T13:33:22.9786640Z [command]/usr/local/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-07-06T13:33:23.1623310Z [command]/usr/local/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-06T13:33:23.1746940Z http.https://github.com/.extraheader
2026-07-06T13:33:23.1763640Z [command]/usr/local/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-07-06T13:33:23.1897870Z [command]/usr/local/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-07-06T13:33:23.3633020Z [command]/usr/local/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-06T13:33:23.3749780Z [command]/usr/local/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-07-06T13:33:23.5610970Z Cleaning up orphan processes
2026-07-06T13:33:25.2862300Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/cache@v4, actions/checkout@v4, actions/setup-java@v4. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 11. `apache__hugegraph__088106696924.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/apache__hugegraph__088106696924.txt` (authoritative; read this, not the excerpt)
- **Repository**: `apache/hugegraph`
- **Content hash (sha256, first 16)**: `c314e9e68eb2bb01`
- **Body size**: 1,529,620 bytes, 10,854 lines
- **Excerpt**: final 120 of 10,854 lines, content-blind

```text
2026-07-18T18:01:10.9901117Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'expired.delete_batch' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9903018Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9904900Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'expired.delete_batch' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9906732Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9908584Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'expired.delete_batch' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9910713Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9912940Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'expired.delete_batch' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9914879Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9939489Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'expired.delete_batch' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9942131Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9943985Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'expired.delete_batch' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9945850Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9954339Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'expired.delete_batch' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9956291Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9973722Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'expired.delete_batch' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9975586Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9979912Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'expired.delete_batch' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9982211Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9994488Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'expired.delete_batch' is redundant, please ensure it has been registered
2026-07-18T18:01:10.9996552Z 2026-07-18 18:01:10 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-07-18T18:01:11.0023604Z 2026-07-18 18:01:11 [main] [WARN] o.a.h.c.HugeConfig - The config option 'expired.delete_batch' is redundant, please ensure it has been registered
2026-07-18T18:01:11.0025441Z 2026-07-18 18:01:11 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-07-18T18:01:11.0041535Z 2026-07-18 18:01:11 [main] [WARN] o.a.h.c.HugeConfig - The config option 'expired.delete_batch' is redundant, please ensure it has been registered
2026-07-18T18:01:11.0045641Z 2026-07-18 18:01:11 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-07-18T18:01:11.0047230Z 2026-07-18 18:01:11 [main] [WARN] o.a.h.c.HugeConfig - The config option 'expired.delete_batch' is redundant, please ensure it has been registered
2026-07-18T18:01:11.0048568Z 2026-07-18 18:01:11 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-07-18T18:01:11.0050036Z 2026-07-18 18:01:11 [main] [WARN] o.a.h.c.HugeConfig - The config option 'expired.delete_batch' is redundant, please ensure it has been registered
2026-07-18T18:01:11.0051573Z 2026-07-18 18:01:11 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-07-18T18:01:12.2589841Z 2026-07-18 18:01:12 [main] [INFO] o.a.h.StandardHugeGraph - Graph 'DEFAULT-hugegraph' has been cleared
2026-07-18T18:01:12.2591670Z 2026-07-18 18:01:12 [main] [INFO] o.a.h.StandardHugeGraph - Close graph standardhugegraph[DEFAULT-hugegraph]
2026-07-18T18:01:12.2783133Z [ERROR] Tests run: 798, Failures: 1, Errors: 0, Skipped: 41, Time elapsed: 420.376 s <<< FAILURE! - in org.apache.hugegraph.core.CoreTestSuite
2026-07-18T18:01:12.2785223Z [ERROR] testQueryByNonEqLabelAndIndexedProperty(org.apache.hugegraph.core.VertexCoreTest)  Time elapsed: 0.577 s  <<< FAILURE!
2026-07-18T18:01:12.2787697Z java.lang.AssertionError: No exception was thrown(expected org.apache.hugegraph.exception.NoIndexException)
2026-07-18T18:01:12.2789571Z 	at org.apache.hugegraph.core.VertexCoreTest.testQueryByNonEqLabelAndIndexedProperty(VertexCoreTest.java:9100)
2026-07-18T18:01:12.2790990Z 
2026-07-18T18:01:12.2819259Z 2026-07-18 18:01:12 [hugegraph-shutdown] [INFO] o.a.h.HugeFactory - HugeGraph is shutting down
2026-07-18T18:01:12.3729457Z 2026-07-18 18:01:12 [hugegraph-shutdown] [INFO] o.a.h.HugeFactory - HugeFactory shutdown
2026-07-18T18:01:12.7266573Z [INFO] 
2026-07-18T18:01:12.7266942Z [INFO] Results:
2026-07-18T18:01:12.7267285Z [INFO] 
2026-07-18T18:01:12.7267646Z [ERROR] Failures: 
2026-07-18T18:01:12.7268946Z [ERROR]   VertexCoreTest.testQueryByNonEqLabelAndIndexedProperty:9100 No exception was thrown(expected org.apache.hugegraph.exception.NoIndexException)
2026-07-18T18:01:12.7270547Z [INFO] 
2026-07-18T18:01:12.7271384Z [ERROR] Tests run: 798, Failures: 1, Errors: 0, Skipped: 41
2026-07-18T18:01:12.7271793Z [INFO] 
2026-07-18T18:01:12.7282840Z [INFO] ------------------------------------------------------------------------
2026-07-18T18:01:12.7283597Z [INFO] Reactor Summary for hugegraph 1.7.0:
2026-07-18T18:01:12.7284063Z [INFO] 
2026-07-18T18:01:12.7284605Z [INFO] hugegraph .......................................... SUCCESS [  1.314 s]
2026-07-18T18:01:12.7285724Z [INFO] hugegraph-commons .................................. SUCCESS [  1.005 s]
2026-07-18T18:01:12.7286948Z [INFO] hugegraph-common ................................... SUCCESS [  4.798 s]
2026-07-18T18:01:12.7287984Z [INFO] hugegraph-pd ....................................... SUCCESS [  0.338 s]
2026-07-18T18:01:12.7288787Z [INFO] hg-pd-grpc ......................................... SUCCESS [  8.286 s]
2026-07-18T18:01:12.7289557Z [INFO] hg-pd-common ....................................... SUCCESS [  0.171 s]
2026-07-18T18:01:12.7290632Z [INFO] hg-pd-client ....................................... SUCCESS [  1.563 s]
2026-07-18T18:01:12.7291269Z [INFO] hugegraph-struct ................................... SUCCESS [  2.116 s]
2026-07-18T18:01:12.7291756Z [INFO] hugegraph-store .................................... SUCCESS [  0.099 s]
2026-07-18T18:01:12.7292225Z [INFO] hg-store-common .................................... SUCCESS [  0.576 s]
2026-07-18T18:01:12.7292683Z [INFO] hugegraph-server ................................... SUCCESS [  0.216 s]
2026-07-18T18:01:12.7293136Z [INFO] hugegraph-core ..................................... SUCCESS [  9.594 s]
2026-07-18T18:01:12.7293579Z [INFO] hugegraph-rpc ...................................... SUCCESS [  0.514 s]
2026-07-18T18:01:12.7294027Z [INFO] hugegraph-api ...................................... SUCCESS [  1.932 s]
2026-07-18T18:01:12.7294494Z [INFO] hugegraph-cassandra ................................ SUCCESS [  0.986 s]
2026-07-18T18:01:12.7301235Z [INFO] hugegraph-scylladb ................................. SUCCESS [  0.597 s]
2026-07-18T18:01:12.7301749Z [INFO] hugegraph-rocksdb .................................. SUCCESS [  0.580 s]
2026-07-18T18:01:12.7302235Z [INFO] hugegraph-mysql .................................... SUCCESS [  0.502 s]
2026-07-18T18:01:12.7302682Z [INFO] hugegraph-palo ..................................... SUCCESS [  0.605 s]
2026-07-18T18:01:12.7303135Z [INFO] hugegraph-hbase .................................... SUCCESS [  0.861 s]
2026-07-18T18:01:12.7303588Z [INFO] hugegraph-postgresql ............................... SUCCESS [  0.702 s]
2026-07-18T18:01:12.7304032Z [INFO] hg-store-grpc ...................................... SUCCESS [  3.539 s]
2026-07-18T18:01:12.7304776Z [INFO] hg-store-client .................................... SUCCESS [  0.376 s]
2026-07-18T18:01:12.7305228Z [INFO] hugegraph-hstore ................................... SUCCESS [  0.718 s]
2026-07-18T18:01:12.7306026Z [INFO] hugegraph-dist ..................................... SUCCESS [  0.780 s]
2026-07-18T18:01:12.7306480Z [INFO] hugegraph-test ..................................... FAILURE [07:08 min]
2026-07-18T18:01:12.7307099Z [INFO] ------------------------------------------------------------------------
2026-07-18T18:01:12.7307440Z [INFO] BUILD FAILURE
2026-07-18T18:01:12.7307727Z [INFO] ------------------------------------------------------------------------
2026-07-18T18:01:12.7308067Z [INFO] Total time:  07:51 min
2026-07-18T18:01:12.7308325Z [INFO] Finished at: 2026-07-18T18:01:12Z
2026-07-18T18:01:12.7308809Z [INFO] ------------------------------------------------------------------------
2026-07-18T18:01:12.7310438Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.20:test (core-test) on project hugegraph-test: There are test failures.
2026-07-18T18:01:12.7311517Z [ERROR] 
2026-07-18T18:01:12.7312614Z [ERROR] Please refer to /home/runner/work/hugegraph/hugegraph/hugegraph-server/hugegraph-test/target/surefire-reports for the individual test results.
2026-07-18T18:01:12.7313990Z [ERROR] Please refer to dump files (if any exist) [date]-jvmRun[N].dump, [date].dumpstream and [date]-jvmRun[N].dumpstream.
2026-07-18T18:01:12.7314532Z [ERROR] -> [Help 1]
2026-07-18T18:01:12.7314731Z [ERROR] 
2026-07-18T18:01:12.7315041Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-07-18T18:01:12.7315522Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-07-18T18:01:12.7315866Z [ERROR] 
2026-07-18T18:01:12.7316635Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-07-18T18:01:12.7317571Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
2026-07-18T18:01:12.7318130Z [ERROR] 
2026-07-18T18:01:12.7318712Z [ERROR] After correcting the problems, you can resume the build with the command
2026-07-18T18:01:12.7319312Z [ERROR]   mvn <args> -rf :hugegraph-test
2026-07-18T18:01:12.7876176Z ##[error]Process completed with exit code 1.
2026-07-18T18:01:12.7998160Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-07-18T18:01:12.7999484Z Post job cleanup.
2026-07-18T18:01:12.9331905Z (node:10155) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-07-18T18:01:12.9333257Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-07-18T18:01:12.9490814Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-07-18T18:01:12.9492078Z Post job cleanup.
2026-07-18T18:01:13.0955463Z (node:10163) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-07-18T18:01:13.0956393Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-07-18T18:01:13.1119228Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-07-18T18:01:13.1120645Z Post job cleanup.
2026-07-18T18:01:13.2001694Z [command]/usr/bin/git version
2026-07-18T18:01:13.2041100Z git version 2.54.0
2026-07-18T18:01:13.2083364Z Temporarily overriding HOME='/home/runner/work/_temp/6426a238-7ba5-4d57-a215-8b0819a38dc8' before making global git config changes
2026-07-18T18:01:13.2084185Z Adding repository directory to the temporary git global config as a safe directory
2026-07-18T18:01:13.2090240Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/hugegraph/hugegraph
2026-07-18T18:01:13.2129046Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-07-18T18:01:13.2163858Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-07-18T18:01:13.2418864Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-18T18:01:13.2443064Z http.https://github.com/.extraheader
2026-07-18T18:01:13.2454298Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-07-18T18:01:13.2487084Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-07-18T18:01:13.2737972Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-18T18:01:13.2772308Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-07-18T18:01:13.3271541Z Cleaning up orphan processes
2026-07-18T18:01:13.3657808Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/cache@v4, actions/checkout@v4, actions/setup-java@v4. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 12. `apache__tika__087468230709.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/apache__tika__087468230709.txt` (authoritative; read this, not the excerpt)
- **Repository**: `apache/tika`
- **Content hash (sha256, first 16)**: `784c94472abdd558`
- **Body size**: 277,842 bytes, 2,650 lines
- **Excerpt**: final 120 of 2,650 lines, content-blind

```text
2026-07-15T20:48:09.2533929Z [INFO] Apache Tika transcribe aws ......................... SKIPPED
2026-07-15T20:48:09.2534515Z [INFO] Apache Tika bundles module ......................... SKIPPED
2026-07-15T20:48:09.2535087Z [INFO] Apache Tika OSGi standard bundle ................... SKIPPED
2026-07-15T20:48:09.2535882Z [INFO] Apache Tika XMP .................................... SKIPPED
2026-07-15T20:48:09.2536460Z [INFO] Apache Tika Lingo24 langdetect ..................... SKIPPED
2026-07-15T20:48:09.2537048Z [INFO] Apache Tika MIT Lincoln Labs langdetect ............ SKIPPED
2026-07-15T20:48:09.2537628Z [INFO] Apache Tika pipes .................................. SKIPPED
2026-07-15T20:48:09.2538197Z [INFO] Apache Tika pipes api .............................. SKIPPED
2026-07-15T20:48:09.2538782Z [INFO] Apache Tika Pipes iterators - base ................. SKIPPED
2026-07-15T20:48:09.2539341Z [INFO] Apache Tika pipes core ............................. SKIPPED
2026-07-15T20:48:09.2540788Z [INFO] Apache Tika httpclient commons ..................... SKIPPED
2026-07-15T20:48:09.2541398Z [INFO] Apache Tika Pipes Reporter - base .................. SKIPPED
2026-07-15T20:48:09.2541975Z [INFO] Apache Tika Plugins ................................ SKIPPED
2026-07-15T20:48:09.2542563Z [INFO] Apache Tika Pipes Atlassian JWT .................... SKIPPED
2026-07-15T20:48:09.2543518Z [INFO] Apache Tika Pipes Azure Blob ....................... SKIPPED
2026-07-15T20:48:09.2553363Z [INFO] Apache Tika Pipes CSV .............................. SKIPPED
2026-07-15T20:48:09.2555661Z [INFO] Apache Tika Pipes File System ...................... SKIPPED
2026-07-15T20:48:09.2556846Z [INFO] Apache Tika Pipes GCS .............................. SKIPPED
2026-07-15T20:48:09.2557498Z [INFO] Apache Tika Pipes Google Drive ..................... SKIPPED
2026-07-15T20:48:09.2558134Z [INFO] Apache Tika Pipes HTTP ............................. SKIPPED
2026-07-15T20:48:09.2558752Z [INFO] Apache Tika Pipes JDBC ............................. SKIPPED
2026-07-15T20:48:09.2559379Z [INFO] Apache Tika Pipes JSON ............................. SKIPPED
2026-07-15T20:48:09.2560006Z [INFO] Apache Tika Pipes Kafka ............................ SKIPPED
2026-07-15T20:48:09.2560633Z [INFO] Apache Tika Pipes Microsoft Graph .................. SKIPPED
2026-07-15T20:48:09.2561296Z [INFO] Apache Tika Pipes Elasticsearch .................... SKIPPED
2026-07-15T20:48:09.2562227Z [INFO] Apache Tika Pipes OpenSearch ....................... SKIPPED
2026-07-15T20:48:09.2562867Z [INFO] Apache Tika Pipes S3 ............................... SKIPPED
2026-07-15T20:48:09.2563496Z [INFO] Apache Tika Pipes Apache Solr ...................... SKIPPED
2026-07-15T20:48:09.2564131Z [INFO] Apache Tika Pipes Config Store Ignite .............. SKIPPED
2026-07-15T20:48:09.2564763Z [INFO] Apache Tika eval module ............................ SKIPPED
2026-07-15T20:48:09.2565378Z [INFO] Apache Tika eval core .............................. SKIPPED
2026-07-15T20:48:09.2566709Z [INFO] Apache Tika pipes fork parser ...................... SKIPPED
2026-07-15T20:48:09.2572470Z [INFO] Apache Tika Async CLI .............................. SKIPPED
2026-07-15T20:48:09.2582433Z [INFO] Apache Tika pipes core integration tests ........... SKIPPED
2026-07-15T20:48:09.2584757Z [INFO] Apache Tika pipes gRPC server ...................... SKIPPED
2026-07-15T20:48:09.2590299Z [INFO] Apache Tika application ............................ SKIPPED
2026-07-15T20:48:09.2591406Z [INFO] Apache Tika translate .............................. SKIPPED
2026-07-15T20:48:09.2592087Z [INFO] Apache Tika server module .......................... SKIPPED
2026-07-15T20:48:09.2592733Z [INFO] Apache Tika server core ............................ SKIPPED
2026-07-15T20:48:09.2596367Z [INFO] Apache Tika standard server ........................ SKIPPED
2026-07-15T20:48:09.2600535Z [INFO] Apache Tika server client .......................... SKIPPED
2026-07-15T20:48:09.2605081Z [INFO] Apache Tika integration tests ...................... SKIPPED
2026-07-15T20:48:09.2606126Z [INFO] Apache Tika Elasticsearch integration tests ........ SKIPPED
2026-07-15T20:48:09.2610184Z [INFO] Apache Tika OpenSearch integration tests ........... SKIPPED
2026-07-15T20:48:09.2610956Z [INFO] Apache Tika Apache Solr integration tests .......... SKIPPED
2026-07-15T20:48:09.2611932Z [INFO] Apache Tika S3 pipes integration tests ............. SKIPPED
2026-07-15T20:48:09.2612625Z [INFO] Apache Tika Kafka pipes integration tests .......... SKIPPED
2026-07-15T20:48:09.2613306Z [INFO] tika-resource-loading-tests ........................ SKIPPED
2026-07-15T20:48:09.2613956Z [INFO] tika-woodstox-tests ................................ SKIPPED
2026-07-15T20:48:09.2614585Z [INFO] Apache Tika eval application ....................... SKIPPED
2026-07-15T20:48:09.2615217Z [INFO] Apache Tika examples ............................... SKIPPED
2026-07-15T20:48:09.2615862Z [INFO] Apache Tika Java-7 Components ...................... SKIPPED
2026-07-15T20:48:09.2616510Z [INFO] Apache Tika End-to-End Tests ....................... SKIPPED
2026-07-15T20:48:09.2617169Z [INFO] Apache Tika gRPC End-to-End Tests .................. SKIPPED
2026-07-15T20:48:09.2625117Z [INFO] Apache Tika E2E Tests: REST Server ................. SKIPPED
2026-07-15T20:48:09.2625842Z [INFO] Apache Tika ........................................ SKIPPED
2026-07-15T20:48:09.2626540Z [INFO] ------------------------------------------------------------------------
2026-07-15T20:48:09.2627105Z [INFO] BUILD FAILURE
2026-07-15T20:48:09.2627559Z [INFO] ------------------------------------------------------------------------
2026-07-15T20:48:09.2628134Z [INFO] Total time:  01:24 min
2026-07-15T20:48:09.2628516Z [INFO] Finished at: 2026-07-15T20:48:09Z
2026-07-15T20:48:09.2629048Z [INFO] ------------------------------------------------------------------------
2026-07-15T20:48:09.2630058Z [ERROR] Failed to execute goal com.diffplug.spotless:spotless-maven-plugin:3.8.0:check (default) on project tika-parser-audiovideo-module: The following files had format violations:
2026-07-15T20:48:09.2630892Z [ERROR]     src\test\java\org\apache\tika\parser\mp4\MP4ParserTest.java
2026-07-15T20:48:09.2631275Z [ERROR]         @@ -17,8 +17,8 @@
2026-07-15T20:48:09.2632274Z [ERROR]          package�org.apache.tika.parser.mp4;
2026-07-15T20:48:09.2632616Z [ERROR]          
2026-07-15T20:48:09.2633034Z [ERROR]          import�static�org.junit.jupiter.api.Assertions.assertEquals;
2026-07-15T20:48:09.2633861Z [ERROR]         +import�static�org.junit.jupiter.api.Assertions.assertFalse;
2026-07-15T20:48:09.2634399Z [ERROR]          import�static�org.junit.jupiter.api.Assertions.assertNull;
2026-07-15T20:48:09.2634928Z [ERROR]         -import�static�org.junit.jupiter.api.Assertions.assertFalse;
2026-07-15T20:48:09.2635457Z [ERROR]          import�static�org.junit.jupiter.api.Assertions.assertTrue;
2026-07-15T20:48:09.2635809Z [ERROR]          
2026-07-15T20:48:09.2636100Z [ERROR]          import�java.io.ByteArrayOutputStream;
2026-07-15T20:48:09.2636471Z [ERROR] Run 'mvn spotless:apply' to fix these violations.
2026-07-15T20:48:09.2636767Z [ERROR] -> [Help 1]
2026-07-15T20:48:09.2636951Z [ERROR] 
2026-07-15T20:48:09.2637262Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-07-15T20:48:09.2637740Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-07-15T20:48:09.2638074Z [ERROR] 
2026-07-15T20:48:09.2638455Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-07-15T20:48:09.2639072Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoExecutionException
2026-07-15T20:48:09.2639459Z [ERROR] 
2026-07-15T20:48:09.2639772Z [ERROR] After correcting the problems, you can resume the build with the command
2026-07-15T20:48:09.2640206Z [ERROR]   mvn <args> -rf :tika-parser-audiovideo-module
2026-07-15T20:48:09.6266122Z ##[error]Process completed with exit code 1.
2026-07-15T20:48:09.6516590Z Post job cleanup.
2026-07-15T20:48:09.8429384Z Post job cleanup.
2026-07-15T20:48:10.0367092Z [command]"C:\Program Files\Git\bin\git.exe" version
2026-07-15T20:48:10.0658524Z git version 2.55.0.windows.2
2026-07-15T20:48:10.0733620Z Temporarily overriding HOME='D:\a\_temp\67c649b4-1916-452a-aa24-0342f758ced3' before making global git config changes
2026-07-15T20:48:10.0734766Z Adding repository directory to the temporary git global config as a safe directory
2026-07-15T20:48:10.0744490Z [command]"C:\Program Files\Git\bin\git.exe" config --global --add safe.directory D:\a\tika\tika
2026-07-15T20:48:10.1109121Z Removing SSH command configuration
2026-07-15T20:48:10.1123612Z [command]"C:\Program Files\Git\bin\git.exe" config --local --name-only --get-regexp core\.sshCommand
2026-07-15T20:48:10.1522179Z [command]"C:\Program Files\Git\bin\git.exe" submodule foreach --recursive "sh -c \"git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :\""
2026-07-15T20:48:10.7462505Z Removing HTTP extra header
2026-07-15T20:48:10.7472461Z [command]"C:\Program Files\Git\bin\git.exe" config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-15T20:48:10.7771679Z [command]"C:\Program Files\Git\bin\git.exe" submodule foreach --recursive "sh -c \"git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :\""
2026-07-15T20:48:11.3270939Z Removing includeIf entries pointing to credentials config files
2026-07-15T20:48:11.3282704Z [command]"C:\Program Files\Git\bin\git.exe" config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-15T20:48:11.3541452Z includeif.gitdir:D:/a/tika/tika/.git.path
2026-07-15T20:48:11.3542032Z includeif.gitdir:D:/a/tika/tika/.git/worktrees/*.path
2026-07-15T20:48:11.3542571Z includeif.gitdir:/github/workspace/.git.path
2026-07-15T20:48:11.3543172Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-15T20:48:11.3582326Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all includeif.gitdir:D:/a/tika/tika/.git.path
2026-07-15T20:48:11.3834193Z D:\a\_temp\git-credentials-e557b25c-b65f-4b47-a2f1-9f4f2c7496ba.config
2026-07-15T20:48:11.3875005Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset includeif.gitdir:D:/a/tika/tika/.git.path D:\a\_temp\git-credentials-e557b25c-b65f-4b47-a2f1-9f4f2c7496ba.config
2026-07-15T20:48:11.4166392Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all includeif.gitdir:D:/a/tika/tika/.git/worktrees/*.path
2026-07-15T20:48:11.4416893Z D:\a\_temp\git-credentials-e557b25c-b65f-4b47-a2f1-9f4f2c7496ba.config
2026-07-15T20:48:11.4458406Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset includeif.gitdir:D:/a/tika/tika/.git/worktrees/*.path D:\a\_temp\git-credentials-e557b25c-b65f-4b47-a2f1-9f4f2c7496ba.config
2026-07-15T20:48:11.4759026Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-07-15T20:48:11.5011134Z /github/runner_temp/git-credentials-e557b25c-b65f-4b47-a2f1-9f4f2c7496ba.config
2026-07-15T20:48:11.5050044Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset includeif.gitdir:/github/workspace/.git.path /github/runner_temp/git-credentials-e557b25c-b65f-4b47-a2f1-9f4f2c7496ba.config
2026-07-15T20:48:11.5341034Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-15T20:48:11.5590795Z /github/runner_temp/git-credentials-e557b25c-b65f-4b47-a2f1-9f4f2c7496ba.config
2026-07-15T20:48:11.5633033Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path /github/runner_temp/git-credentials-e557b25c-b65f-4b47-a2f1-9f4f2c7496ba.config
2026-07-15T20:48:11.5924898Z [command]"C:\Program Files\Git\bin\git.exe" submodule foreach --recursive "git config --local --show-origin --name-only --get-regexp remote.origin.url"
2026-07-15T20:48:12.1374575Z Removing credentials config 'D:\a\_temp\git-credentials-e557b25c-b65f-4b47-a2f1-9f4f2c7496ba.config'
2026-07-15T20:48:12.1572281Z Cleaning up orphan processes
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 13. `apache__tika__093653111110.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/apache__tika__093653111110.txt` (authoritative; read this, not the excerpt)
- **Repository**: `apache/tika`
- **Content hash (sha256, first 16)**: `764155991895664d`
- **Body size**: 2,381,683 bytes, 20,463 lines
- **Excerpt**: final 120 of 20,463 lines, content-blind

```text
2026-08-11T02:02:13.2754612Z [INFO] Apache Tika scientific parser package .............. SUCCESS [  8.877 s]
2026-08-11T02:02:13.2754796Z [INFO] Apache Tika extended parser integration tests ...... SUCCESS [ 11.414 s]
2026-08-11T02:02:13.2754983Z [INFO] Apache Tika machine learning (ml) parsers .......... SUCCESS [  0.189 s]
2026-08-11T02:02:13.2755165Z [INFO] Apache Tika natural language process module ........ SUCCESS [ 11.633 s]
2026-08-11T02:02:13.2755356Z [INFO] Apache Tika natural language processing package .... SUCCESS [  3.888 s]
2026-08-11T02:02:13.2755535Z [INFO] Apache Tika inference module ....................... SUCCESS [  6.979 s]
2026-08-11T02:02:13.2755702Z [INFO] Apache Tika VLM module ............................. SUCCESS [  8.034 s]
2026-08-11T02:02:13.2755882Z [INFO] Apache Tika Tess4J OCR parser module ............... SUCCESS [  6.226 s]
2026-08-11T02:02:13.2756122Z [INFO] Apache Tika transcribe aws ......................... SUCCESS [  6.055 s]
2026-08-11T02:02:13.2756305Z [INFO] Apache Tika metadata schema ........................ FAILURE [ 12.186 s]
2026-08-11T02:02:13.2756460Z [INFO] Apache Tika bundles module ......................... SKIPPED
2026-08-11T02:02:13.2756647Z [INFO] Apache Tika OSGi standard bundle ................... SKIPPED
2026-08-11T02:02:13.2756792Z [INFO] Apache Tika XMP .................................... SKIPPED
2026-08-11T02:02:13.2756943Z [INFO] Apache Tika Lingo24 langdetect ..................... SKIPPED
2026-08-11T02:02:13.2757086Z [INFO] Apache Tika MIT Lincoln Labs langdetect ............ SKIPPED
2026-08-11T02:02:13.2757225Z [INFO] Apache Tika pipes .................................. SKIPPED
2026-08-11T02:02:13.2757361Z [INFO] Apache Tika pipes api .............................. SKIPPED
2026-08-11T02:02:13.2757510Z [INFO] Apache Tika Pipes iterators - base ................. SKIPPED
2026-08-11T02:02:13.2757655Z [INFO] Apache Tika pipes core ............................. SKIPPED
2026-08-11T02:02:13.2757837Z [INFO] Apache Tika httpclient commons ..................... SKIPPED
2026-08-11T02:02:13.2757996Z [INFO] Apache Tika Pipes Reporter - base .................. SKIPPED
2026-08-11T02:02:13.2758137Z [INFO] Apache Tika Plugins ................................ SKIPPED
2026-08-11T02:02:13.2758280Z [INFO] Apache Tika Pipes Atlassian JWT .................... SKIPPED
2026-08-11T02:02:13.2758427Z [INFO] Apache Tika Pipes Azure Blob ....................... SKIPPED
2026-08-11T02:02:13.2758559Z [INFO] Apache Tika Pipes CSV .............................. SKIPPED
2026-08-11T02:02:13.2758701Z [INFO] Apache Tika Pipes File System ...................... SKIPPED
2026-08-11T02:02:13.2758841Z [INFO] Apache Tika Pipes GCS .............................. SKIPPED
2026-08-11T02:02:13.2758980Z [INFO] Apache Tika Pipes Google Drive ..................... SKIPPED
2026-08-11T02:02:13.2759121Z [INFO] Apache Tika Pipes HTTP ............................. SKIPPED
2026-08-11T02:02:13.2759327Z [INFO] Apache Tika Pipes JDBC ............................. SKIPPED
2026-08-11T02:02:13.2759512Z [INFO] Apache Tika Pipes JSON ............................. SKIPPED
2026-08-11T02:02:13.2759655Z [INFO] Apache Tika Pipes Kafka ............................ SKIPPED
2026-08-11T02:02:13.2759797Z [INFO] Apache Tika Pipes Microsoft Graph .................. SKIPPED
2026-08-11T02:02:13.2759946Z [INFO] Apache Tika Pipes Elasticsearch .................... SKIPPED
2026-08-11T02:02:13.2760083Z [INFO] Apache Tika Pipes OpenSearch ....................... SKIPPED
2026-08-11T02:02:13.2760223Z [INFO] Apache Tika Pipes S3 ............................... SKIPPED
2026-08-11T02:02:13.2760367Z [INFO] Apache Tika Pipes Apache Solr ...................... SKIPPED
2026-08-11T02:02:13.2760510Z [INFO] Apache Tika Pipes Config Store Ignite .............. SKIPPED
2026-08-11T02:02:13.2760653Z [INFO] Apache Tika eval module ............................ SKIPPED
2026-08-11T02:02:13.2761246Z [INFO] Apache Tika eval core .............................. SKIPPED
2026-08-11T02:02:13.2761428Z [INFO] Apache Tika pipes fork parser ...................... SKIPPED
2026-08-11T02:02:13.2761566Z [INFO] Apache Tika Async CLI .............................. SKIPPED
2026-08-11T02:02:13.2761710Z [INFO] Apache Tika pipes core integration tests ........... SKIPPED
2026-08-11T02:02:13.2761860Z [INFO] Apache Tika pipes gRPC server ...................... SKIPPED
2026-08-11T02:02:13.2762005Z [INFO] Apache Tika application ............................ SKIPPED
2026-08-11T02:02:13.2762145Z [INFO] Apache Tika translate .............................. SKIPPED
2026-08-11T02:02:13.2762290Z [INFO] Apache Tika server module .......................... SKIPPED
2026-08-11T02:02:13.2762424Z [INFO] Apache Tika server core ............................ SKIPPED
2026-08-11T02:02:13.2762570Z [INFO] Apache Tika standard server ........................ SKIPPED
2026-08-11T02:02:13.2762713Z [INFO] Apache Tika server client .......................... SKIPPED
2026-08-11T02:02:13.2762949Z [INFO] Apache Tika integration tests ...................... SKIPPED
2026-08-11T02:02:13.2763121Z [INFO] Apache Tika Elasticsearch integration tests ........ SKIPPED
2026-08-11T02:02:13.2763272Z [INFO] Apache Tika OpenSearch integration tests ........... SKIPPED
2026-08-11T02:02:13.2763468Z [INFO] Apache Tika Apache Solr integration tests .......... SKIPPED
2026-08-11T02:02:13.2763626Z [INFO] Apache Tika S3 pipes integration tests ............. SKIPPED
2026-08-11T02:02:13.2763770Z [INFO] Apache Tika Kafka pipes integration tests .......... SKIPPED
2026-08-11T02:02:13.2763931Z [INFO] tika-resource-loading-tests ........................ SKIPPED
2026-08-11T02:02:13.2764078Z [INFO] tika-woodstox-tests ................................ SKIPPED
2026-08-11T02:02:13.2764220Z [INFO] Apache Tika eval application ....................... SKIPPED
2026-08-11T02:02:13.2764359Z [INFO] Apache Tika examples ............................... SKIPPED
2026-08-11T02:02:13.2764509Z [INFO] Apache Tika Java-7 Components ...................... SKIPPED
2026-08-11T02:02:13.2764659Z [INFO] Apache Tika End-to-End Tests ....................... SKIPPED
2026-08-11T02:02:13.2764797Z [INFO] Apache Tika gRPC End-to-End Tests .................. SKIPPED
2026-08-11T02:02:13.2764945Z [INFO] Apache Tika E2E Tests: REST Server ................. SKIPPED
2026-08-11T02:02:13.2765081Z [INFO] Apache Tika ........................................ SKIPPED
2026-08-11T02:02:13.2765231Z [INFO] ------------------------------------------------------------------------
2026-08-11T02:02:13.2765311Z [INFO] BUILD FAILURE
2026-08-11T02:02:13.2765461Z [INFO] ------------------------------------------------------------------------
2026-08-11T02:02:13.2765550Z [INFO] Total time:  15:01 min
2026-08-11T02:02:13.2765647Z [INFO] Finished at: 2026-08-11T02:02:13Z
2026-08-11T02:02:13.2765793Z [INFO] ------------------------------------------------------------------------
2026-08-11T02:02:13.2766396Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.5.6:test (default-test) on project tika-metadata-schema: There are test failures.
2026-08-11T02:02:13.2766503Z [ERROR] 
2026-08-11T02:02:13.2766885Z [ERROR] See D:\a\tika\tika\tika build dir\tika-metadata-schema\target\surefire-reports for the individual test results.
2026-08-11T02:02:13.2767154Z [ERROR] See dump files (if any exist) [date].dump, [date]-jvmRun[N].dump and [date].dumpstream.
2026-08-11T02:02:13.2767226Z [ERROR] -> [Help 1]
2026-08-11T02:02:13.2767295Z [ERROR] 
2026-08-11T02:02:13.2767518Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-08-11T02:02:13.2767713Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-08-11T02:02:13.2767784Z [ERROR] 
2026-08-11T02:02:13.2768103Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-08-11T02:02:13.2768364Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
2026-08-11T02:02:13.2768440Z [ERROR] 
2026-08-11T02:02:13.2768662Z [ERROR] After correcting the problems, you can resume the build with the command
2026-08-11T02:02:13.2768856Z [ERROR]   mvn <args> -rf :tika-metadata-schema
2026-08-11T02:02:13.5078400Z ##[error]Process completed with exit code 1.
2026-08-11T02:02:13.5377423Z Post job cleanup.
2026-08-11T02:02:13.7374289Z Post job cleanup.
2026-08-11T02:02:13.9683909Z [command]"C:\Program Files\Git\bin\git.exe" version
2026-08-11T02:02:14.0012445Z git version 2.55.0.windows.3
2026-08-11T02:02:14.0092161Z Temporarily overriding HOME='D:\a\_temp\fc0aa673-84a2-4118-8e55-23a55a9748c0' before making global git config changes
2026-08-11T02:02:14.0093495Z Adding repository directory to the temporary git global config as a safe directory
2026-08-11T02:02:14.0105557Z [command]"C:\Program Files\Git\bin\git.exe" config --global --add safe.directory "D:\a\tika\tika\tika build dir"
2026-08-11T02:02:14.0443381Z Removing SSH command configuration
2026-08-11T02:02:14.0456199Z [command]"C:\Program Files\Git\bin\git.exe" config --local --name-only --get-regexp core\.sshCommand
2026-08-11T02:02:14.0828478Z [command]"C:\Program Files\Git\bin\git.exe" submodule foreach --recursive "sh -c \"git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :\""
2026-08-11T02:02:14.6943513Z Removing HTTP extra header
2026-08-11T02:02:14.6954229Z [command]"C:\Program Files\Git\bin\git.exe" config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-08-11T02:02:14.7282406Z [command]"C:\Program Files\Git\bin\git.exe" submodule foreach --recursive "sh -c \"git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :\""
2026-08-11T02:02:15.3036179Z Removing includeIf entries pointing to credentials config files
2026-08-11T02:02:15.3047939Z [command]"C:\Program Files\Git\bin\git.exe" config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-08-11T02:02:15.3336778Z includeif.gitdir:D:/a/tika/tika/tika build dir/.git.path
2026-08-11T02:02:15.3337550Z includeif.gitdir:D:/a/tika/tika/tika build dir/.git/worktrees/*.path
2026-08-11T02:02:15.3338287Z includeif.gitdir:/github/workspace/tika build dir/.git.path
2026-08-11T02:02:15.3339063Z includeif.gitdir:/github/workspace/tika build dir/.git/worktrees/*.path
2026-08-11T02:02:15.3377896Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all "includeif.gitdir:D:/a/tika/tika/tika build dir/.git.path"
2026-08-11T02:02:15.3641957Z D:\a\_temp\git-credentials-8632f012-fe3c-4caf-8a54-bf4785504252.config
2026-08-11T02:02:15.3686267Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset "includeif.gitdir:D:/a/tika/tika/tika build dir/.git.path" D:\a\_temp\git-credentials-8632f012-fe3c-4caf-8a54-bf4785504252.config
2026-08-11T02:02:15.3993426Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all "includeif.gitdir:D:/a/tika/tika/tika build dir/.git/worktrees/*.path"
2026-08-11T02:02:15.4266077Z D:\a\_temp\git-credentials-8632f012-fe3c-4caf-8a54-bf4785504252.config
2026-08-11T02:02:15.4308638Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset "includeif.gitdir:D:/a/tika/tika/tika build dir/.git/worktrees/*.path" D:\a\_temp\git-credentials-8632f012-fe3c-4caf-8a54-bf4785504252.config
2026-08-11T02:02:15.4628222Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all "includeif.gitdir:/github/workspace/tika build dir/.git.path"
2026-08-11T02:02:15.4901326Z /github/runner_temp/git-credentials-8632f012-fe3c-4caf-8a54-bf4785504252.config
2026-08-11T02:02:15.4941877Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset "includeif.gitdir:/github/workspace/tika build dir/.git.path" /github/runner_temp/git-credentials-8632f012-fe3c-4caf-8a54-bf4785504252.config
2026-08-11T02:02:15.5262829Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all "includeif.gitdir:/github/workspace/tika build dir/.git/worktrees/*.path"
2026-08-11T02:02:15.5530805Z /github/runner_temp/git-credentials-8632f012-fe3c-4caf-8a54-bf4785504252.config
2026-08-11T02:02:15.5575335Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset "includeif.gitdir:/github/workspace/tika build dir/.git/worktrees/*.path" /github/runner_temp/git-credentials-8632f012-fe3c-4caf-8a54-bf4785504252.config
2026-08-11T02:02:15.5907393Z [command]"C:\Program Files\Git\bin\git.exe" submodule foreach --recursive "git config --local --show-origin --name-only --get-regexp remote.origin.url"
2026-08-11T02:02:16.1614350Z Removing credentials config 'D:\a\_temp\git-credentials-8632f012-fe3c-4caf-8a54-bf4785504252.config'
2026-08-11T02:02:16.1834806Z Cleaning up orphan processes
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 14. `apache__zeppelin__087393956477.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/apache__zeppelin__087393956477.txt` (authoritative; read this, not the excerpt)
- **Repository**: `apache/zeppelin`
- **Content hash (sha256, first 16)**: `2a6dfd08663fed81`
- **Body size**: 1,065,016 bytes, 9,294 lines
- **Excerpt**: final 120 of 9,294 lines, content-blind

```text
2026-07-15T15:41:01.3040452Z 15:41:01,274  WARN org.apache.zeppelin.interpreter.remote.ExecRemoteInterpreterProcess:231 - Process is exited with exit value 0
2026-07-15T15:41:01.3041120Z 15:41:01,274  INFO org.apache.zeppelin.interpreter.util.ProcessLauncher:108 - Process state is transitioned to COMPLETED
2026-07-15T15:41:01.3041786Z 15:41:01,277  WARN org.apache.zeppelin.interpreter.remote.ExecRemoteInterpreterProcess:231 - Process is exited with exit value 0
2026-07-15T15:41:01.3042526Z 15:41:01,277  INFO org.apache.zeppelin.interpreter.util.ProcessLauncher:108 - Process state is transitioned to COMPLETED
2026-07-15T15:41:01.3990489Z 15:41:01,312  INFO org.apache.zeppelin.scheduler.SchedulerFactory:116 - Remove scheduler: RemoteInterpreter-spark-shared_process-shared_session
2026-07-15T15:41:01.3992161Z 15:41:01,313  INFO org.apache.zeppelin.interpreter.ManagedInterpreterGroup:109 - Remove this InterpreterGroup: spark-shared_process as all the sessions are closed
2026-07-15T15:41:01.3993721Z 15:41:01,313  INFO org.apache.zeppelin.interpreter.ManagedInterpreterGroup:112 - Kill RemoteInterpreterProcess
2026-07-15T15:41:01.3994683Z 15:41:01,313  INFO org.apache.zeppelin.interpreter.remote.RemoteInterpreterManagedProcess:80 - Stop interpreter process for interpreter group: spark-shared_process
2026-07-15T15:41:01.3995683Z 15:41:01,316  INFO org.apache.zeppelin.interpreter.RemoteInterpreterEventServer:190 - Unregister interpreter process: spark-shared_process
2026-07-15T15:41:01.3996892Z 15:41:01,316  WARN org.apache.zeppelin.interpreter.RemoteInterpreterEventServer:194 - Unable to unregister interpreter process because no such interpreterGroup: spark-shared_process
2026-07-15T15:41:01.3997926Z 15:41:01,351  WARN org.apache.zeppelin.interpreter.remote.ExecRemoteInterpreterProcess:231 - Process is exited with exit value 0
2026-07-15T15:41:01.3998798Z 15:41:01,351  INFO org.apache.zeppelin.interpreter.util.ProcessLauncher:108 - Process state is transitioned to COMPLETED
2026-07-15T15:41:03.8013096Z 15:41:03,763  INFO org.apache.zeppelin.interpreter.remote.ExecRemoteInterpreterProcess:136 - Remote exec process of interpreter group: sh-shared_process is terminated
2026-07-15T15:41:03.8014321Z 15:41:03,766  INFO org.apache.zeppelin.interpreter.remote.ExecRemoteInterpreterProcess:136 - Remote exec process of interpreter group: md-shared_process is terminated
2026-07-15T15:41:03.9014750Z 15:41:03,818  INFO org.apache.zeppelin.interpreter.remote.ExecRemoteInterpreterProcess:136 - Remote exec process of interpreter group: spark-shared_process is terminated
2026-07-15T15:41:03.9015861Z 15:41:03,818  INFO org.apache.zeppelin.notebook.repo.NotebookRepoSync:424 - Closing all notebook storages
2026-07-15T15:41:03.9016443Z 15:41:03,819  INFO org.apache.zeppelin.server.ZeppelinServer:370 - Bye
2026-07-15T15:41:05.8369929Z 15:41:05,820  INFO org.apache.zeppelin.MiniZeppelinServer:305 - ZeppelinServerMock terminated.
2026-07-15T15:41:05.8427464Z [WARNING] Tests run: 21, Failures: 0, Errors: 0, Skipped: 3, Time elapsed: 270.1 s -- in org.apache.zeppelin.integration.ParagraphActionsIT
2026-07-15T15:41:06.1860257Z [INFO] 
2026-07-15T15:41:06.1860585Z [INFO] Results:
2026-07-15T15:41:06.1860843Z [INFO] 
2026-07-15T15:41:06.1861072Z [ERROR] Errors: 
2026-07-15T15:41:06.1869933Z [ERROR]   AuthenticationIT.testSimpleAuthentication:96->AbstractZeppelinIT.authenticationUser:56 » ElementClickIntercepted element click intercepted: Element <button class="btn nav-login-btn" data-toggle="modal" data-target="#loginModal" ng-click="navbar.showLoginWindow()">...</button> is not clickable at point (1869, 25). Other element would receive the click: <div id="loginModal" class="modal fade ng-scope in" role="dialog" tabindex="-1" style="display: block;">...</div>
2026-07-15T15:41:06.1871339Z   (Session info: chrome=150.0.7871.114)
2026-07-15T15:41:06.1871620Z Build info: version: '4.20.0', revision: '866c76ca80'
2026-07-15T15:41:06.1872031Z System info: os.name: 'Linux', os.arch: 'amd64', os.version: '6.17.0-1020-azure', java.version: '11.0.31'
2026-07-15T15:41:06.1894095Z Driver info: org.openqa.selenium.chrome.ChromeDriver
2026-07-15T15:41:06.1894875Z Command: [7a6813181ceb7c34a100135f999ba5ef, clickElement {id=f.03D0B01D45D88269CA059EEC64EE3B68.d.6A76AECE49963A20194E18A27035D05F.e.22}]
2026-07-15T15:41:06.1925776Z Capabilities {acceptInsecureCerts: false, browserName: chrome, browserVersion: 150.0.7871.114, chrome: {chromedriverVersion: 150.0.7871.115 (25f5b661e5b..., userDataDir: /tmp/org.chromium.Chromium....}, fedcm:accounts: true, goog:chromeOptions: {debuggerAddress: localhost:36629}, goog:processID: 3194, networkConnectionEnabled: false, pageLoadStrategy: normal, platformName: linux, proxy: Proxy(), se:cdp: ws://localhost:36629/devtoo..., se:cdpVersion: 150.0.7871.114, setWindowRect: true, strictFileInteractability: false, timeouts: {implicit: 0, pageLoad: 300000, script: 30000}, unhandledPromptBehavior: dismiss and notify, webauthn:extension:credBlob: true, webauthn:extension:largeBlob: true, webauthn:extension:minPinLength: true, webauthn:extension:prf: true, webauthn:virtualAuthenticators: true}
2026-07-15T15:41:06.1928114Z Element: [[ChromeDriver: chrome on linux (7a6813181ceb7c34a100135f999ba5ef)] -> xpath: //div[contains(@class, 'navbar-collapse')]//li//button[contains(.,'Login')]]
2026-07-15T15:41:06.1928648Z Session ID: 7a6813181ceb7c34a100135f999ba5ef
2026-07-15T15:41:06.1928890Z [INFO] 
2026-07-15T15:41:06.1929107Z [ERROR] Tests run: 39, Failures: 0, Errors: 1, Skipped: 9
2026-07-15T15:41:06.1929476Z [INFO] 
2026-07-15T15:41:06.1948350Z [INFO] 
2026-07-15T15:41:06.1948810Z [INFO] --- failsafe:3.3.0:verify (default) @ zeppelin-integration ---
2026-07-15T15:41:06.2408853Z [INFO] ------------------------------------------------------------------------
2026-07-15T15:41:06.2409245Z [INFO] BUILD FAILURE
2026-07-15T15:41:06.2409565Z [INFO] ------------------------------------------------------------------------
2026-07-15T15:41:06.2409988Z [INFO] Total time:  09:46 min
2026-07-15T15:41:06.2411666Z [INFO] Finished at: 2026-07-15T15:41:06Z
2026-07-15T15:41:06.2412360Z [INFO] ------------------------------------------------------------------------
2026-07-15T15:41:06.2413077Z [WARNING] The requested profile "spark-3.5" could not be activated because it does not exist.
2026-07-15T15:41:06.2414009Z [WARNING] The requested profile "web-dist" could not be activated because it does not exist.
2026-07-15T15:41:06.2419112Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-failsafe-plugin:3.3.0:verify (default) on project zeppelin-integration: 
2026-07-15T15:41:06.2420017Z [ERROR] 
2026-07-15T15:41:06.2420773Z [ERROR] Please refer to /home/runner/work/zeppelin/zeppelin/zeppelin-integration/target/failsafe-reports for the individual test results.
2026-07-15T15:41:06.2421928Z [ERROR] Please refer to dump files (if any exist) [date].dump, [date]-jvmRun[N].dump and [date].dumpstream.
2026-07-15T15:41:06.2422609Z [ERROR] -> [Help 1]
2026-07-15T15:41:06.2422892Z [ERROR] 
2026-07-15T15:41:06.2423488Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-07-15T15:41:06.2424166Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-07-15T15:41:06.2424641Z [ERROR] 
2026-07-15T15:41:06.2425242Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-07-15T15:41:06.2426115Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
2026-07-15T15:41:06.2726151Z ##[error]Process completed with exit code 1.
2026-07-15T15:41:06.2762736Z ##[group]Run if [ -d "logs" ]; then cat logs/*; fi
2026-07-15T15:41:06.2763058Z [36;1mif [ -d "logs" ]; then cat logs/*; fi[0m
2026-07-15T15:41:06.2795593Z shell: /usr/bin/bash -l {0}
2026-07-15T15:41:06.2795834Z env:
2026-07-15T15:41:06.2796400Z   MAVEN_OPTS: -Xms1024M -Xmx2048M -XX:MaxMetaspaceSize=1024m -XX:-UseGCOverheadLimit -Dhttp.keepAlive=false -Dmaven.wagon.http.pool=false -Dmaven.wagon.http.retryHandler.count=3
2026-07-15T15:41:06.2797027Z   MAVEN_ARGS: -B --no-transfer-progress
2026-07-15T15:41:06.2797278Z   ZEPPELIN_HELIUM_REGISTRY: helium
2026-07-15T15:41:06.2797506Z   SPARK_PRINT_LAUNCH_COMMAND: true
2026-07-15T15:41:06.2797721Z   SPARK_LOCAL_IP: 127.0.0.1
2026-07-15T15:41:06.2797931Z   ZEPPELIN_LOCAL_IP: 127.0.0.1
2026-07-15T15:41:06.2798331Z   INTERPRETERS: !hbase,!jdbc,!file,!flink,!cassandra,!elasticsearch,!bigquery,!livy,!groovy,!java,!neo4j,!sparql,!mongodb
2026-07-15T15:41:06.2798823Z   ZEPPELIN_E2E_TEST_NOTEBOOK_DIR: /tmp/zeppelin-e2e-notebooks
2026-07-15T15:41:06.2799239Z   JAVA_HOME: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/11.0.31-11/x64
2026-07-15T15:41:06.2799646Z   JAVA_HOME_11_X64: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/11.0.31-11/x64
2026-07-15T15:41:06.2799964Z   INPUT_RUN_POST: true
2026-07-15T15:41:06.2800167Z   CONDA: /usr/share/miniconda
2026-07-15T15:41:06.2800372Z ##[endgroup]
2026-07-15T15:41:07.5090383Z Post job cleanup.
2026-07-15T15:41:07.6220304Z Post job cleanup.
2026-07-15T15:41:07.6904037Z [command]/usr/bin/git version
2026-07-15T15:41:07.6940070Z git version 2.54.0
2026-07-15T15:41:07.6975882Z Temporarily overriding HOME='/home/runner/work/_temp/a4eb0c1b-9e31-4ffe-9d5c-c1b8405346f2' before making global git config changes
2026-07-15T15:41:07.6977080Z Adding repository directory to the temporary git global config as a safe directory
2026-07-15T15:41:07.6980488Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/zeppelin/zeppelin
2026-07-15T15:41:07.7016298Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-07-15T15:41:07.7047775Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-07-15T15:41:07.7248098Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-15T15:41:07.7264328Z http.https://github.com/.extraheader
2026-07-15T15:41:07.7272518Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-07-15T15:41:07.7296748Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-07-15T15:41:07.7459421Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-15T15:41:07.7480245Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-07-15T15:41:07.7730320Z Cleaning up orphan processes
2026-07-15T15:41:07.7955488Z Terminate orphan process: pid (3179) (chromedriver)
2026-07-15T15:41:07.7979246Z Terminate orphan process: pid (3363) (chromedriver)
2026-07-15T15:41:07.7999942Z Terminate orphan process: pid (3816) (chromedriver)
2026-07-15T15:41:07.8190455Z Terminate orphan process: pid (4117) (chromedriver)
2026-07-15T15:41:07.8217136Z Terminate orphan process: pid (4342) (chromedriver)
2026-07-15T15:41:07.8242948Z Terminate orphan process: pid (4716) (chromedriver)
2026-07-15T15:41:07.8274327Z Terminate orphan process: pid (5139) (chromedriver)
2026-07-15T15:41:07.8296725Z Terminate orphan process: pid (5712) (chromedriver)
2026-07-15T15:41:07.8316467Z Terminate orphan process: pid (6212) (chromedriver)
2026-07-15T15:41:07.8336382Z Terminate orphan process: pid (6549) (chromedriver)
2026-07-15T15:41:07.8356496Z Terminate orphan process: pid (6747) (chromedriver)
2026-07-15T15:41:07.8375865Z Terminate orphan process: pid (7001) (chromedriver)
2026-07-15T15:41:07.8395720Z Terminate orphan process: pid (7221) (chromedriver)
2026-07-15T15:41:07.8415229Z Terminate orphan process: pid (7715) (chromedriver)
2026-07-15T15:41:07.8436833Z Terminate orphan process: pid (7910) (chromedriver)
2026-07-15T15:41:07.8459286Z Terminate orphan process: pid (8180) (chromedriver)
2026-07-15T15:41:07.8481144Z Terminate orphan process: pid (8369) (chromedriver)
2026-07-15T15:41:07.8510875Z Terminate orphan process: pid (8561) (chromedriver)
2026-07-15T15:41:07.8530712Z Terminate orphan process: pid (8758) (chromedriver)
2026-07-15T15:41:07.8559047Z Terminate orphan process: pid (9125) (chromedriver)
2026-07-15T15:41:07.8586703Z Terminate orphan process: pid (9632) (chromedriver)
2026-07-15T15:41:07.8608504Z Terminate orphan process: pid (9831) (chromedriver)
2026-07-15T15:41:07.8628764Z Terminate orphan process: pid (10024) (chromedriver)
2026-07-15T15:41:07.8654048Z Terminate orphan process: pid (10222) (chromedriver)
2026-07-15T15:41:07.8674086Z Terminate orphan process: pid (10494) (chromedriver)
2026-07-15T15:41:07.8696360Z Terminate orphan process: pid (10788) (chromedriver)
2026-07-15T15:41:07.8722254Z Terminate orphan process: pid (11064) (chromedriver)
2026-07-15T15:41:07.8748276Z Terminate orphan process: pid (11260) (chromedriver)
2026-07-15T15:41:07.8770440Z Terminate orphan process: pid (11452) (chromedriver)
2026-07-15T15:41:07.8793254Z Terminate orphan process: pid (11656) (chromedriver)
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 15. `apache__zeppelin__093702538653.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/apache__zeppelin__093702538653.txt` (authoritative; read this, not the excerpt)
- **Repository**: `apache/zeppelin`
- **Content hash (sha256, first 16)**: `f5f3a098754451c7`
- **Body size**: 1,066,005 bytes, 9,711 lines
- **Excerpt**: final 120 of 9,711 lines, content-blind

```text
2026-08-11T07:20:49.2860032Z 07:20:49,216  INFO org.apache.zeppelin.interpreter.ManagedInterpreterGroup:152 - Remove this InterpreterGroup: sh-shared_process as all the sessions are closed
2026-08-11T07:20:49.2860653Z 07:20:49,216  INFO org.apache.zeppelin.interpreter.ManagedInterpreterGroup:155 - Kill RemoteInterpreterProcess
2026-08-11T07:20:49.2861305Z 07:20:49,216  INFO org.apache.zeppelin.interpreter.remote.RemoteInterpreterManagedProcess:80 - Stop interpreter process for interpreter group: sh-shared_process
2026-08-11T07:20:49.2862079Z 07:20:49,217  INFO org.apache.zeppelin.interpreter.RemoteInterpreterEventServer:190 - Unregister interpreter process: md-shared_process
2026-08-11T07:20:49.2862806Z 07:20:49,217  WARN org.apache.zeppelin.interpreter.RemoteInterpreterEventServer:194 - Unable to unregister interpreter process because no such interpreterGroup: md-shared_process
2026-08-11T07:20:49.2863551Z 07:20:49,227  INFO org.apache.zeppelin.interpreter.RemoteInterpreterEventServer:190 - Unregister interpreter process: sh-shared_process
2026-08-11T07:20:49.2864275Z 07:20:49,227  WARN org.apache.zeppelin.interpreter.RemoteInterpreterEventServer:194 - Unable to unregister interpreter process because no such interpreterGroup: sh-shared_process
2026-08-11T07:20:49.2864984Z 07:20:49,249  WARN org.apache.zeppelin.interpreter.remote.ExecRemoteInterpreterProcess:231 - Process is exited with exit value 0
2026-08-11T07:20:49.2865566Z 07:20:49,249  INFO org.apache.zeppelin.interpreter.util.ProcessLauncher:108 - Process state is transitioned to COMPLETED
2026-08-11T07:20:49.2866140Z 07:20:49,260  WARN org.apache.zeppelin.interpreter.remote.ExecRemoteInterpreterProcess:231 - Process is exited with exit value 0
2026-08-11T07:20:49.2866724Z 07:20:49,260  INFO org.apache.zeppelin.interpreter.util.ProcessLauncher:108 - Process state is transitioned to COMPLETED
2026-08-11T07:20:49.3811950Z 07:20:49,287  INFO org.apache.zeppelin.scheduler.SchedulerFactory:116 - Remove scheduler: RemoteInterpreter-spark-shared_process-shared_session
2026-08-11T07:20:49.3812722Z 07:20:49,287  INFO org.apache.zeppelin.interpreter.ManagedInterpreterGroup:152 - Remove this InterpreterGroup: spark-shared_process as all the sessions are closed
2026-08-11T07:20:49.3813370Z 07:20:49,287  INFO org.apache.zeppelin.interpreter.ManagedInterpreterGroup:155 - Kill RemoteInterpreterProcess
2026-08-11T07:20:49.3814004Z 07:20:49,287  INFO org.apache.zeppelin.interpreter.remote.RemoteInterpreterManagedProcess:80 - Stop interpreter process for interpreter group: spark-shared_process
2026-08-11T07:20:49.3814723Z 07:20:49,291  INFO org.apache.zeppelin.interpreter.RemoteInterpreterEventServer:190 - Unregister interpreter process: spark-shared_process
2026-08-11T07:20:49.3815455Z 07:20:49,291  WARN org.apache.zeppelin.interpreter.RemoteInterpreterEventServer:194 - Unable to unregister interpreter process because no such interpreterGroup: spark-shared_process
2026-08-11T07:20:49.3816170Z 07:20:49,337  WARN org.apache.zeppelin.interpreter.remote.ExecRemoteInterpreterProcess:231 - Process is exited with exit value 0
2026-08-11T07:20:49.3816751Z 07:20:49,337  INFO org.apache.zeppelin.interpreter.util.ProcessLauncher:108 - Process state is transitioned to COMPLETED
2026-08-11T07:20:51.7838036Z 07:20:51,730  INFO org.apache.zeppelin.interpreter.remote.ExecRemoteInterpreterProcess:136 - Remote exec process of interpreter group: md-shared_process is terminated
2026-08-11T07:20:51.7839179Z 07:20:51,733  INFO org.apache.zeppelin.interpreter.remote.ExecRemoteInterpreterProcess:136 - Remote exec process of interpreter group: sh-shared_process is terminated
2026-08-11T07:20:51.8840221Z 07:20:51,794  INFO org.apache.zeppelin.interpreter.remote.ExecRemoteInterpreterProcess:136 - Remote exec process of interpreter group: spark-shared_process is terminated
2026-08-11T07:20:51.8841276Z 07:20:51,795  INFO org.apache.zeppelin.notebook.repo.NotebookRepoSync:424 - Closing all notebook storages
2026-08-11T07:20:51.8841752Z 07:20:51,795  INFO org.apache.zeppelin.server.ZeppelinServer:370 - Bye
2026-08-11T07:20:53.8157286Z 07:20:53,797  INFO org.apache.zeppelin.MiniZeppelinServer:305 - ZeppelinServerMock terminated.
2026-08-11T07:20:53.8220421Z [WARNING] Tests run: 21, Failures: 0, Errors: 0, Skipped: 3, Time elapsed: 263.2 s -- in org.apache.zeppelin.integration.ParagraphActionsIT
2026-08-11T07:20:54.1632181Z [INFO] 
2026-08-11T07:20:54.1632406Z [INFO] Results:
2026-08-11T07:20:54.1632635Z [INFO] 
2026-08-11T07:20:54.1635008Z [ERROR] Errors: 
2026-08-11T07:20:54.1635927Z [ERROR]   AuthenticationIT.testAnyOfRolesUser:146  Expected ngToast not found
2026-08-11T07:20:54.1638893Z [INFO] 
2026-08-11T07:20:54.1639465Z [ERROR] Tests run: 39, Failures: 0, Errors: 1, Skipped: 8
2026-08-11T07:20:54.1639804Z [INFO] 
2026-08-11T07:20:54.1699617Z [INFO] 
2026-08-11T07:20:54.1700039Z [INFO] --- failsafe:3.3.0:verify (default) @ zeppelin-integration ---
2026-08-11T07:20:54.2180456Z [INFO] ------------------------------------------------------------------------
2026-08-11T07:20:54.2181234Z [INFO] BUILD FAILURE
2026-08-11T07:20:54.2181946Z [INFO] ------------------------------------------------------------------------
2026-08-11T07:20:54.2182440Z [INFO] Total time:  10:33 min
2026-08-11T07:20:54.2182815Z [INFO] Finished at: 2026-08-11T07:20:54Z
2026-08-11T07:20:54.2183407Z [INFO] ------------------------------------------------------------------------
2026-08-11T07:20:54.2184170Z [WARNING] The requested profile "spark-3.5" could not be activated because it does not exist.
2026-08-11T07:20:54.2185023Z [WARNING] The requested profile "web-dist" could not be activated because it does not exist.
2026-08-11T07:20:54.2209384Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-failsafe-plugin:3.3.0:verify (default) on project zeppelin-integration: 
2026-08-11T07:20:54.2231673Z [ERROR] 
2026-08-11T07:20:54.2248941Z [ERROR] Please refer to /home/runner/work/zeppelin/zeppelin/zeppelin-integration/target/failsafe-reports for the individual test results.
2026-08-11T07:20:54.2250112Z [ERROR] Please refer to dump files (if any exist) [date].dump, [date]-jvmRun[N].dump and [date].dumpstream.
2026-08-11T07:20:54.2250698Z [ERROR] -> [Help 1]
2026-08-11T07:20:54.2250956Z [ERROR] 
2026-08-11T07:20:54.2251374Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-08-11T07:20:54.2252019Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-08-11T07:20:54.2252449Z [ERROR] 
2026-08-11T07:20:54.2252996Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-08-11T07:20:54.2253839Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
2026-08-11T07:20:54.2507436Z ##[error]Process completed with exit code 1.
2026-08-11T07:20:54.2567544Z ##[group]Run if [ -d "logs" ]; then cat logs/*; fi
2026-08-11T07:20:54.2567857Z [36;1mif [ -d "logs" ]; then cat logs/*; fi[0m
2026-08-11T07:20:54.2592916Z shell: /usr/bin/bash -l {0}
2026-08-11T07:20:54.2593129Z env:
2026-08-11T07:20:54.2593685Z   MAVEN_OPTS: -Xms1024M -Xmx2048M -XX:MaxMetaspaceSize=1024m -XX:-UseGCOverheadLimit -Dhttp.keepAlive=false -Dmaven.wagon.http.pool=false -Dmaven.wagon.http.retryHandler.count=3
2026-08-11T07:20:54.2594298Z   MAVEN_ARGS: -B --no-transfer-progress
2026-08-11T07:20:54.2594527Z   ZEPPELIN_HELIUM_REGISTRY: helium
2026-08-11T07:20:54.2594736Z   SPARK_PRINT_LAUNCH_COMMAND: true
2026-08-11T07:20:54.2594943Z   SPARK_LOCAL_IP: 127.0.0.1
2026-08-11T07:20:54.2595133Z   ZEPPELIN_LOCAL_IP: 127.0.0.1
2026-08-11T07:20:54.2595521Z   INTERPRETERS: !hbase,!jdbc,!file,!flink,!cassandra,!elasticsearch,!bigquery,!livy,!groovy,!java,!neo4j,!sparql,!mongodb
2026-08-11T07:20:54.2595997Z   ZEPPELIN_E2E_TEST_NOTEBOOK_DIR: /tmp/zeppelin-e2e-notebooks
2026-08-11T07:20:54.2596394Z   JAVA_HOME: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/11.0.31-11/x64
2026-08-11T07:20:54.2596906Z   JAVA_HOME_11_X64: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/11.0.31-11/x64
2026-08-11T07:20:54.2597210Z   INPUT_RUN_POST: true
2026-08-11T07:20:54.2597398Z   CONDA: /usr/share/miniconda
2026-08-11T07:20:54.2597591Z ##[endgroup]
2026-08-11T07:20:55.3124101Z Post job cleanup.
2026-08-11T07:20:55.4143089Z Post job cleanup.
2026-08-11T07:20:55.4744660Z [command]/usr/bin/git version
2026-08-11T07:20:55.4801519Z git version 2.54.0
2026-08-11T07:20:55.4823861Z Temporarily overriding HOME='/home/runner/work/_temp/304c3c94-a4d4-4249-9773-9aec9fb702f3' before making global git config changes
2026-08-11T07:20:55.4824618Z Adding repository directory to the temporary git global config as a safe directory
2026-08-11T07:20:55.4827206Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/zeppelin/zeppelin
2026-08-11T07:20:55.4852920Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-08-11T07:20:55.4875855Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-08-11T07:20:55.5024295Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-08-11T07:20:55.5040200Z http.https://github.com/.extraheader
2026-08-11T07:20:55.5046783Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-08-11T07:20:55.5067151Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-08-11T07:20:55.5211633Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-08-11T07:20:55.5232134Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-08-11T07:20:55.5460917Z Cleaning up orphan processes
2026-08-11T07:20:55.5650434Z Terminate orphan process: pid (3383) (chromedriver)
2026-08-11T07:20:55.5679626Z Terminate orphan process: pid (3566) (chromedriver)
2026-08-11T07:20:55.5703455Z Terminate orphan process: pid (4029) (chromedriver)
2026-08-11T07:20:55.5722408Z Terminate orphan process: pid (4365) (chromedriver)
2026-08-11T07:20:55.5746232Z Terminate orphan process: pid (4861) (chromedriver)
2026-08-11T07:20:55.5764421Z Terminate orphan process: pid (5118) (chromedriver)
2026-08-11T07:20:55.5782710Z Terminate orphan process: pid (5333) (chromedriver)
2026-08-11T07:20:55.5806737Z Terminate orphan process: pid (5592) (chromedriver)
2026-08-11T07:20:55.5829837Z Terminate orphan process: pid (5809) (chromedriver)
2026-08-11T07:20:55.5849532Z Terminate orphan process: pid (6193) (chromedriver)
2026-08-11T07:20:55.5866897Z Terminate orphan process: pid (6633) (chromedriver)
2026-08-11T07:20:55.5884427Z Terminate orphan process: pid (7204) (chromedriver)
2026-08-11T07:20:55.5909086Z Terminate orphan process: pid (7693) (chromedriver)
2026-08-11T07:20:55.5927925Z Terminate orphan process: pid (7926) (chromedriver)
2026-08-11T07:20:55.5948954Z Terminate orphan process: pid (8413) (chromedriver)
2026-08-11T07:20:55.5972047Z Terminate orphan process: pid (8611) (chromedriver)
2026-08-11T07:20:55.5989357Z Terminate orphan process: pid (8880) (chromedriver)
2026-08-11T07:20:55.6006585Z Terminate orphan process: pid (9082) (chromedriver)
2026-08-11T07:20:55.6029129Z Terminate orphan process: pid (9276) (chromedriver)
2026-08-11T07:20:55.6053706Z Terminate orphan process: pid (9477) (chromedriver)
2026-08-11T07:20:55.6071802Z Terminate orphan process: pid (9836) (chromedriver)
2026-08-11T07:20:55.6092009Z Terminate orphan process: pid (10283) (chromedriver)
2026-08-11T07:20:55.6111814Z Terminate orphan process: pid (10482) (chromedriver)
2026-08-11T07:20:55.6135450Z Terminate orphan process: pid (10673) (chromedriver)
2026-08-11T07:20:55.6159946Z Terminate orphan process: pid (10879) (chromedriver)
2026-08-11T07:20:55.6184804Z Terminate orphan process: pid (11145) (chromedriver)
2026-08-11T07:20:55.6204541Z Terminate orphan process: pid (11446) (chromedriver)
2026-08-11T07:20:55.6227063Z Terminate orphan process: pid (11739) (chromedriver)
2026-08-11T07:20:55.6244677Z Terminate orphan process: pid (11929) (chromedriver)
2026-08-11T07:20:55.6262086Z Terminate orphan process: pid (12123) (chromedriver)
2026-08-11T07:20:55.6280349Z Terminate orphan process: pid (12321) (chromedriver)
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 16. `apple__servicetalk__093415674647.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/apple__servicetalk__093415674647.txt` (authoritative; read this, not the excerpt)
- **Repository**: `apple/servicetalk`
- **Content hash (sha256, first 16)**: `5845470fade3b424`
- **Body size**: 277,301 bytes, 3,166 lines
- **Excerpt**: final 120 of 3,166 lines, content-blind

```text
2026-08-10T09:54:05.5182611Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3330.jsonl.
2026-08-10T09:54:05.5212960Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--7826.jsonl.
2026-08-10T09:54:05.5243123Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5846.jsonl.
2026-08-10T09:54:05.5270544Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--7994.jsonl.
2026-08-10T09:54:05.5304631Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5040.jsonl.
2026-08-10T09:54:05.5343832Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3702.jsonl.
2026-08-10T09:54:05.5376781Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--6039.jsonl.
2026-08-10T09:54:05.5415881Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--4056.jsonl.
2026-08-10T09:54:05.5436255Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3273.jsonl.
2026-08-10T09:54:05.5472067Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--4483.jsonl.
2026-08-10T09:54:05.5503214Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--8139.jsonl.
2026-08-10T09:54:05.5518543Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3952.jsonl.
2026-08-10T09:54:05.5576876Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--7540.jsonl.
2026-08-10T09:54:05.5598365Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--4754.jsonl.
2026-08-10T09:54:05.5626648Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--4404.jsonl.
2026-08-10T09:54:05.5644145Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5210.jsonl.
2026-08-10T09:54:05.5677210Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5230.jsonl.
2026-08-10T09:54:05.5697101Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5933.jsonl.
2026-08-10T09:54:05.5721859Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--8220.jsonl.
2026-08-10T09:54:05.5744717Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5266.jsonl.
2026-08-10T09:54:05.5766839Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3071.jsonl.
2026-08-10T09:54:05.5806531Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3524.jsonl.
2026-08-10T09:54:05.5840026Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5447.jsonl.
2026-08-10T09:54:05.5867319Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3308.jsonl.
2026-08-10T09:54:05.5886575Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--8074.jsonl.
2026-08-10T09:54:05.5916339Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--7412.jsonl.
2026-08-10T09:54:05.5926498Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3605.jsonl.
2026-08-10T09:54:05.5948044Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--4299.jsonl.
2026-08-10T09:54:05.5985737Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--4442.jsonl.
2026-08-10T09:54:05.5987408Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5706.jsonl.
2026-08-10T09:54:05.6026561Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--6962.jsonl.
2026-08-10T09:54:05.6056434Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--7657.jsonl.
2026-08-10T09:54:05.6079995Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--6444.jsonl.
2026-08-10T09:54:05.6084253Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--2766.jsonl.
2026-08-10T09:54:05.6110755Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5701.jsonl.
2026-08-10T09:54:05.6156504Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--7600.jsonl.
2026-08-10T09:54:05.6158138Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--6651.jsonl.
2026-08-10T09:54:05.6186545Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3143.jsonl.
2026-08-10T09:54:05.6216480Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3195.jsonl.
2026-08-10T09:54:05.6246407Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--8308.jsonl.
2026-08-10T09:54:05.6276485Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--6059.jsonl.
2026-08-10T09:54:05.6282130Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5894.jsonl.
2026-08-10T09:54:05.6300984Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3809.jsonl.
2026-08-10T09:54:05.6317570Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--8166.jsonl.
2026-08-10T09:54:05.6348461Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3229.jsonl.
2026-08-10T09:54:05.6363968Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--4841.jsonl.
2026-08-10T09:54:05.6386595Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--6371.jsonl.
2026-08-10T09:54:05.6416681Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--6162.jsonl.
2026-08-10T09:54:05.6426423Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3009.jsonl.
2026-08-10T09:54:05.6445681Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3918.jsonl.
2026-08-10T09:54:05.6456873Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--8582.jsonl.
2026-08-10T09:54:05.6463682Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--6269.jsonl.
2026-08-10T09:54:05.6487668Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--4141.jsonl.
2026-08-10T09:54:05.6506614Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5104.jsonl.
2026-08-10T09:54:05.6536510Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--6215.jsonl.
2026-08-10T09:54:05.6544360Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--4060.jsonl.
2026-08-10T09:54:05.6566115Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--6830.jsonl.
2026-08-10T09:54:05.6585796Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--8445.jsonl.
2026-08-10T09:54:05.6604991Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--4326.jsonl.
2026-08-10T09:54:05.6646589Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--6609.jsonl.
2026-08-10T09:54:05.6667187Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--6641.jsonl.
2026-08-10T09:54:05.6668934Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3389.jsonl.
2026-08-10T09:54:05.6693813Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3678.jsonl.
2026-08-10T09:54:05.6726492Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--7520.jsonl.
2026-08-10T09:54:05.6756041Z Looking for diagnostics in /home/runner/work/_temp/codeql_databases/diagnostic...
2026-08-10T09:54:05.6783029Z Found diagnostics file /home/runner/work/_temp/codeql_databases/diagnostic/cli-diagnostics-add-20260810T094638.128Z.json.
2026-08-10T09:54:05.6806388Z Looking for diagnostics in /home/runner/work/_temp/codeql_databases/diagnostic/tracer...
2026-08-10T09:54:05.6816569Z Found 120 raw diagnostic messages.
2026-08-10T09:54:05.7055088Z Will only interpret the first 50 results for the diagnostic 'Java extractor telemetry', which had a total of 118 results.
2026-08-10T09:54:05.7060403Z Processed diagnostic messages (removed 68 due to limits, created 0 summary diagnostics for status page).
2026-08-10T09:54:05.7079197Z Interpreted diagnostic messages (448ms).
2026-08-10T09:54:05.8293154Z Uploading failed SARIF file ../codeql-failed-run.sarif
2026-08-10T09:54:05.8295420Z Post-processing sarif files: ["../codeql-failed-run.sarif"]
2026-08-10T09:54:05.8309512Z Adding fingerprints to SARIF file. See https://docs.github.com/en/code-security/reference/code-scanning/sarif-support-for-code-scanning#data-for-preventing-duplicated-alerts for more information.
2026-08-10T09:54:05.8313172Z ##[group]Uploading code scanning results
2026-08-10T09:54:05.8596654Z Uploading results
2026-08-10T09:54:06.4043654Z Successfully uploaded results
2026-08-10T09:54:06.4044417Z ##[endgroup]
2026-08-10T09:54:06.4045769Z ##[group]Waiting for processing to finish
2026-08-10T09:54:11.5649540Z Analysis upload status is failed.
2026-08-10T09:54:11.5651286Z Successfully uploaded a SARIF file for the unsuccessful execution. Received expected "unsuccessful execution" processing error, and no other errors.
2026-08-10T09:54:11.5652701Z ##[endgroup]
2026-08-10T09:54:11.5724678Z CodeQL job status was configuration error.
2026-08-10T09:54:11.5796671Z Sending status report for init-post step.
2026-08-10T09:54:11.7101951Z Status report sent for init-post step.
2026-08-10T09:54:11.7359830Z Post job cleanup.
2026-08-10T09:54:11.8767719Z Post job cleanup.
2026-08-10T09:54:11.9673406Z [command]/usr/bin/git version
2026-08-10T09:54:11.9731367Z git version 2.54.0
2026-08-10T09:54:11.9783301Z Temporarily overriding HOME='/home/runner/work/_temp/9ab7d96f-f509-42b4-a8c6-32930ba46f6f' before making global git config changes
2026-08-10T09:54:11.9785124Z Adding repository directory to the temporary git global config as a safe directory
2026-08-10T09:54:11.9792237Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/servicetalk/servicetalk
2026-08-10T09:54:11.9847102Z Removing SSH command configuration
2026-08-10T09:54:11.9856300Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-08-10T09:54:11.9915072Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-08-10T09:54:12.0398666Z Removing HTTP extra header
2026-08-10T09:54:12.0406082Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-08-10T09:54:12.0463005Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-08-10T09:54:12.0921166Z Removing includeIf entries pointing to credentials config files
2026-08-10T09:54:12.0932633Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-08-10T09:54:12.0983558Z includeif.gitdir:/home/runner/work/servicetalk/servicetalk/.git.path
2026-08-10T09:54:12.0984758Z includeif.gitdir:/home/runner/work/servicetalk/servicetalk/.git/worktrees/*.path
2026-08-10T09:54:12.0985992Z includeif.gitdir:/github/workspace/.git.path
2026-08-10T09:54:12.0986665Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-08-10T09:54:12.0999304Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/servicetalk/servicetalk/.git.path
2026-08-10T09:54:12.1044693Z /home/runner/work/_temp/git-credentials-411543b0-4943-45a5-bc7b-10c482a7408a.config
2026-08-10T09:54:12.1061221Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/servicetalk/servicetalk/.git.path \/home\/runner\/work\/_temp\/git\-credentials\-411543b0\-4943\-45a5\-bc7b\-10c482a7408a\.config
2026-08-10T09:54:12.1119059Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/servicetalk/servicetalk/.git/worktrees/*.path
2026-08-10T09:54:12.1155656Z /home/runner/work/_temp/git-credentials-411543b0-4943-45a5-bc7b-10c482a7408a.config
2026-08-10T09:54:12.1166795Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/servicetalk/servicetalk/.git/worktrees/*.path \/home\/runner\/work\/_temp\/git\-credentials\-411543b0\-4943\-45a5\-bc7b\-10c482a7408a\.config
2026-08-10T09:54:12.1215829Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-08-10T09:54:12.1253924Z /github/runner_temp/git-credentials-411543b0-4943-45a5-bc7b-10c482a7408a.config
2026-08-10T09:54:12.1265792Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git.path \/github\/runner_temp\/git\-credentials\-411543b0\-4943\-45a5\-bc7b\-10c482a7408a\.config
2026-08-10T09:54:12.1313674Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-08-10T09:54:12.1349196Z /github/runner_temp/git-credentials-411543b0-4943-45a5-bc7b-10c482a7408a.config
2026-08-10T09:54:12.1359919Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path \/github\/runner_temp\/git\-credentials\-411543b0\-4943\-45a5\-bc7b\-10c482a7408a\.config
2026-08-10T09:54:12.1409357Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-08-10T09:54:12.1820324Z Removing credentials config '/home/runner/work/_temp/git-credentials-411543b0-4943-45a5-bc7b-10c482a7408a.config'
2026-08-10T09:54:12.1990358Z Cleaning up orphan processes
2026-08-10T09:54:12.2311068Z Terminate orphan process: pid (2629) (java)
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 17. `apple__servicetalk__094207332011.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/apple__servicetalk__094207332011.txt` (authoritative; read this, not the excerpt)
- **Repository**: `apple/servicetalk`
- **Content hash (sha256, first 16)**: `cf8a027f28a2b925`
- **Body size**: 41,571 bytes, 495 lines
- **Excerpt**: final 120 of 495 lines, content-blind

```text
2026-08-12T17:49:37.0358755Z > Task :servicetalk-examples:http:servicetalk-examples-http-debugging:clean UP-TO-DATE
2026-08-12T17:49:37.0360284Z > Task :servicetalk-examples:http:servicetalk-examples-http-redirects:clean UP-TO-DATE
2026-08-12T17:49:37.0361729Z > Task :servicetalk-examples:http:servicetalk-examples-http-opentracing:clean UP-TO-DATE
2026-08-12T17:49:37.0363176Z > Task :servicetalk-examples:http:servicetalk-examples-http-opentelemetry-tracing:clean UP-TO-DATE
2026-08-12T17:49:37.0365043Z > Task :servicetalk-examples:http:servicetalk-examples-http-service-composition:clean UP-TO-DATE
2026-08-12T17:49:37.0366469Z > Task :servicetalk-examples:http:servicetalk-examples-http-retry:clean UP-TO-DATE
2026-08-12T17:49:37.0367937Z > Task :servicetalk-examples:http:serialization:servicetalk-examples-http-serialization-bytes:clean UP-TO-DATE
2026-08-12T17:49:37.0369428Z > Task :servicetalk-examples:http:servicetalk-examples-http-timeout:clean UP-TO-DATE
2026-08-12T17:49:37.0370911Z > Task :servicetalk-examples:http:serialization:servicetalk-examples-http-serialization-json:clean UP-TO-DATE
2026-08-12T17:49:37.0372446Z > Task :servicetalk-examples:http:servicetalk-examples-http-traffic-resilience:clean UP-TO-DATE
2026-08-12T17:49:37.0374107Z > Task :servicetalk-examples:http:servicetalk-examples-http-uds:clean UP-TO-DATE
2026-08-12T17:49:37.0375603Z > Task :servicetalk-examples:http:serialization:servicetalk-examples-http-serialization-protobuf:clean UP-TO-DATE
2026-08-12T17:49:37.1183663Z 
2026-08-12T17:49:37.1244639Z [Incubating] Problems report is available at: file:///home/runner/work/servicetalk/servicetalk/build/reports/problems/problems-report.html
2026-08-12T17:49:37.1273527Z 
2026-08-12T17:49:37.1274076Z Deprecated Gradle features were used in this build, making it incompatible with Gradle 10.
2026-08-12T17:49:37.1274682Z 
2026-08-12T17:49:37.1275371Z You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.
2026-08-12T17:49:37.1276258Z 
2026-08-12T17:49:37.1277129Z For more on this, please refer to https://docs.gradle.org/9.6.1/userguide/command_line_interface.html#sec:command_line_warnings in the Gradle documentation.
2026-08-12T17:49:37.1278117Z 
2026-08-12T17:49:37.1278285Z BUILD SUCCESSFUL in 15s
2026-08-12T17:49:37.1278800Z 127 actionable tasks: 3 executed, 1 from cache, 123 up-to-date
2026-08-12T17:49:37.1279921Z Consider enabling configuration cache to speed up this build: https://docs.gradle.org/9.6.1/userguide/configuration_cache_enabling.html
2026-08-12T17:49:37.4788225Z ##[group]Run sudo -E env "PATH=$PATH" bash -c "ulimit -l 65536 && ulimit -a && ./gradlew --no-daemon --parallel test"
2026-08-12T17:49:37.4789025Z [36;1msudo -E env "PATH=$PATH" bash -c "ulimit -l 65536 && ulimit -a && ./gradlew --no-daemon --parallel test"[0m
2026-08-12T17:49:37.4831887Z shell: /usr/bin/bash -e {0}
2026-08-12T17:49:37.4832137Z env:
2026-08-12T17:49:37.4832420Z   JAVA_HOME: /opt/hostedtoolcache/Java_Zulu_jdk/17.0.20-8/x64
2026-08-12T17:49:37.4833005Z   JAVA_HOME_17_X64: /opt/hostedtoolcache/Java_Zulu_jdk/17.0.20-8/x64
2026-08-12T17:49:37.4833579Z   MAVEN_ARGS: -ntp
2026-08-12T17:49:37.4833802Z   TEST_JAVA_VERSION: 17
2026-08-12T17:49:37.4834051Z   JAVA_TOOL_OPTIONS: -Dfile.encoding=UTF-8
2026-08-12T17:49:37.4834340Z ##[endgroup]
2026-08-12T17:49:37.4982731Z real-time non-blocking time  (microseconds, -R) unlimited
2026-08-12T17:49:37.4984216Z core file size              (blocks, -c) 0
2026-08-12T17:49:37.4984613Z data seg size               (kbytes, -d) unlimited
2026-08-12T17:49:37.4984951Z scheduling priority                 (-e) 0
2026-08-12T17:49:37.4985264Z file size                   (blocks, -f) unlimited
2026-08-12T17:49:37.4985595Z pending signals                     (-i) 63838
2026-08-12T17:49:37.4985899Z max locked memory           (kbytes, -l) 65536
2026-08-12T17:49:37.4986204Z max memory size             (kbytes, -m) unlimited
2026-08-12T17:49:37.4986529Z open files                          (-n) 1024
2026-08-12T17:49:37.4986834Z pipe size                (512 bytes, -p) 8
2026-08-12T17:49:37.4987141Z POSIX message queues         (bytes, -q) 819200
2026-08-12T17:49:37.4987457Z real-time priority                  (-r) 0
2026-08-12T17:49:37.4987757Z stack size                  (kbytes, -s) 8192
2026-08-12T17:49:37.4988070Z cpu time                   (seconds, -t) unlimited
2026-08-12T17:49:37.4988393Z max user processes                  (-u) 63838
2026-08-12T17:49:37.4988705Z virtual memory              (kbytes, -v) unlimited
2026-08-12T17:49:37.4989022Z file locks                          (-x) unlimited
2026-08-12T17:49:37.5999907Z Fetching distribution (retrying 2 times, with an initial back off of 500 ms).
2026-08-12T17:49:37.6000954Z Downloading https://services.gradle.org/distributions/gradle-9.6.1-all.zip
2026-08-12T17:49:38.2103819Z 
2026-08-12T17:49:38.2107305Z Attempt 1/3 failed. Reason: Unexpected end of file from server
2026-08-12T17:49:38.7112542Z Downloading https://services.gradle.org/distributions/gradle-9.6.1-all.zip
2026-08-12T17:49:38.9866075Z 
2026-08-12T17:49:38.9868118Z Attempt 2/3 failed. Reason: Unexpected end of file from server
2026-08-12T17:49:39.9872218Z Downloading https://services.gradle.org/distributions/gradle-9.6.1-all.zip
2026-08-12T17:49:40.1719930Z 
2026-08-12T17:49:40.1723102Z Attempt 3/3 failed. Reason: Server returned HTTP response code: 503 for URL: https://services.gradle.org/distributions/gradle-9.6.1-all.zip
2026-08-12T17:49:40.1752002Z ##[error]Exception in thread "main" java.io.IOException: Server returned HTTP response code: 503 for URL: https://services.gradle.org/distributions/gradle-9.6.1-all.zip
2026-08-12T17:49:40.1759962Z 	at org.gradle.wrapper.Download.download(SourceFile:1)
2026-08-12T17:49:40.1760402Z 	at org.gradle.wrapper.Install.forceFetch(SourceFile)
2026-08-12T17:49:40.1760873Z 	at org.gradle.wrapper.Install.lambda$createDist$0(SourceFile:9)
2026-08-12T17:49:40.1761326Z 	at org.gradle.wrapper.Install.createDist(SourceFile:24)
2026-08-12T17:49:40.1761847Z 	at org.gradle.wrapper.GradleWrapperMain.lambda$prepareWrapper$0(SourceFile:2)
2026-08-12T17:49:40.1762370Z 	at org.gradle.wrapper.GradleWrapperMain.main(SourceFile:2)
2026-08-12T17:49:40.1810092Z ##[error]Process completed with exit code 1.
2026-08-12T17:49:40.1895215Z ##[group]Run actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a
2026-08-12T17:49:40.1895648Z with:
2026-08-12T17:49:40.1895863Z   name: test-results-ubuntu-17
2026-08-12T17:49:40.1896146Z   path: **/build/test-results/test/TEST-*.xml
2026-08-12T17:49:40.1896441Z   if-no-files-found: warn
2026-08-12T17:49:40.1896687Z   compression-level: 6
2026-08-12T17:49:40.1896916Z   overwrite: false
2026-08-12T17:49:40.1897136Z   include-hidden-files: false
2026-08-12T17:49:40.1897382Z   archive: true
2026-08-12T17:49:40.1897575Z env:
2026-08-12T17:49:40.1897831Z   JAVA_HOME: /opt/hostedtoolcache/Java_Zulu_jdk/17.0.20-8/x64
2026-08-12T17:49:40.1898249Z   JAVA_HOME_17_X64: /opt/hostedtoolcache/Java_Zulu_jdk/17.0.20-8/x64
2026-08-12T17:49:40.1898764Z   MAVEN_ARGS: -ntp
2026-08-12T17:49:40.1898973Z   TEST_JAVA_VERSION: 17
2026-08-12T17:49:40.1899189Z ##[endgroup]
2026-08-12T17:49:40.8996916Z ##[warning]No files were found with the provided path: **/build/test-results/test/TEST-*.xml. No artifacts will be uploaded.
2026-08-12T17:49:40.9173662Z Post job cleanup.
2026-08-12T17:49:41.0489746Z Post job cleanup.
2026-08-12T17:49:41.1291965Z [command]/usr/bin/git version
2026-08-12T17:49:41.1334032Z git version 2.54.0
2026-08-12T17:49:41.1371264Z Temporarily overriding HOME='/home/runner/work/_temp/3c43339f-21f1-4e57-b57f-441293f40124' before making global git config changes
2026-08-12T17:49:41.1372634Z Adding repository directory to the temporary git global config as a safe directory
2026-08-12T17:49:41.1377552Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/servicetalk/servicetalk
2026-08-12T17:49:41.1407602Z Removing SSH command configuration
2026-08-12T17:49:41.1413519Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-08-12T17:49:41.1447598Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-08-12T17:49:41.1671218Z Removing HTTP extra header
2026-08-12T17:49:41.1677998Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-08-12T17:49:41.1709448Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-08-12T17:49:41.1929965Z Removing includeIf entries pointing to credentials config files
2026-08-12T17:49:41.1936406Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-08-12T17:49:41.1961900Z includeif.gitdir:/home/runner/work/servicetalk/servicetalk/.git.path
2026-08-12T17:49:41.1962952Z includeif.gitdir:/home/runner/work/servicetalk/servicetalk/.git/worktrees/*.path
2026-08-12T17:49:41.1964191Z includeif.gitdir:/github/workspace/.git.path
2026-08-12T17:49:41.1964897Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-08-12T17:49:41.1970967Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/servicetalk/servicetalk/.git.path
2026-08-12T17:49:41.1993815Z /home/runner/work/_temp/git-credentials-1a707745-ea36-4bba-a914-b39e4898e4e9.config
2026-08-12T17:49:41.2005661Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/servicetalk/servicetalk/.git.path \/home\/runner\/work\/_temp\/git\-credentials\-1a707745\-ea36\-4bba\-a914\-b39e4898e4e9\.config
2026-08-12T17:49:41.2042470Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/servicetalk/servicetalk/.git/worktrees/*.path
2026-08-12T17:49:41.2065911Z /home/runner/work/_temp/git-credentials-1a707745-ea36-4bba-a914-b39e4898e4e9.config
2026-08-12T17:49:41.2078614Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/servicetalk/servicetalk/.git/worktrees/*.path \/home\/runner\/work\/_temp\/git\-credentials\-1a707745\-ea36\-4bba\-a914\-b39e4898e4e9\.config
2026-08-12T17:49:41.2120775Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-08-12T17:49:41.2142808Z /github/runner_temp/git-credentials-1a707745-ea36-4bba-a914-b39e4898e4e9.config
2026-08-12T17:49:41.2152534Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git.path \/github\/runner_temp\/git\-credentials\-1a707745\-ea36\-4bba\-a914\-b39e4898e4e9\.config
2026-08-12T17:49:41.2185533Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-08-12T17:49:41.2207642Z /github/runner_temp/git-credentials-1a707745-ea36-4bba-a914-b39e4898e4e9.config
2026-08-12T17:49:41.2218744Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path \/github\/runner_temp\/git\-credentials\-1a707745\-ea36\-4bba\-a914\-b39e4898e4e9\.config
2026-08-12T17:49:41.2255069Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-08-12T17:49:41.2496825Z Removing credentials config '/home/runner/work/_temp/git-credentials-1a707745-ea36-4bba-a914-b39e4898e4e9.config'
2026-08-12T17:49:41.2636935Z Cleaning up orphan processes
2026-08-12T17:49:41.2935573Z Terminate orphan process: pid (2295) (java)
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 18. `baomidou__mybatis-plus__083974450312.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/baomidou__mybatis-plus__083974450312.txt` (authoritative; read this, not the excerpt)
- **Repository**: `baomidou/mybatis-plus`
- **Content hash (sha256, first 16)**: `4e00f1214cfd9154`
- **Body size**: 41,261 bytes, 429 lines
- **Excerpt**: final 120 of 429 lines, content-blind

```text
2026-06-29T04:03:47.6023093Z > Task :mybatis-plus-generator:checkKotlinGradlePluginConfigurationErrors SKIPPED
2026-06-29T04:03:47.6632056Z > Task :mybatis-plus-core:generateTestEffectiveLombokConfig
2026-06-29T04:03:52.5613359Z 
2026-06-29T04:03:52.5653192Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/src/test/java/com/baomidou/mybatisplus/core/MethodTest.java:39: warning: [deprecation] SelectPage in com.baomidou.mybatisplus.core.injector.methods has been deprecated
2026-06-29T04:03:52.5655073Z > Task :mybatis-plus-core:compileTestJava
2026-06-29T04:03:52.5711456Z             .add(new SelectPage())
2026-06-29T04:03:52.5715596Z                      ^
2026-06-29T04:03:52.6663168Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/src/test/java/com/baomidou/mybatisplus/core/toolkit/MybatisUtilsTest.java:30: warning: [deprecation] setSqlSessionFactory(SqlSessionFactory) in GlobalConfig has been deprecated
2026-06-29T04:03:52.6742063Z         GlobalConfigUtils.getGlobalConfig(configuration).setSqlSessionFactory(Mockito.mock(SqlSessionFactory.class));
2026-06-29T04:03:52.6784566Z                                                         ^
2026-06-29T04:03:52.9629821Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/src/test/java/com/baomidou/mybatisplus/test/MybatisParameterHandlerTest.java:69: warning: [deprecation] DefaultIdentifierGenerator() in DefaultIdentifierGenerator has been deprecated
2026-06-29T04:03:52.9642422Z         GlobalConfigUtils.getGlobalConfig(configuration).setIdentifierGenerator(new DefaultIdentifierGenerator()).setMetaObjectHandler(new MetaObjectHandler() {
2026-06-29T04:03:52.9671603Z                                                                                 ^
2026-06-29T04:03:53.2622984Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/src/test/java/com/baomidou/mybatisplus/test/metadata/TableInfoHelperTest.java:318: warning: [deprecation] getConfiguration() in TableInfo has been deprecated
2026-06-29T04:03:53.2651949Z         final ResultMap resultMap = tableInfo.getConfiguration().getResultMap(tableInfo.getResultMap());
2026-06-29T04:03:53.2681495Z                                              ^
2026-06-29T04:03:53.2713043Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/src/test/java/com/baomidou/mybatisplus/test/MybatisConfigurationTest.java:38: warning: [deprecation] isMultipleResultSetsEnabled() in Configuration has been deprecated
2026-06-29T04:03:53.2741645Z         Assertions.assertTrue(configuration.isMultipleResultSetsEnabled());
2026-06-29T04:03:53.2751485Z                                            ^
2026-06-29T04:03:53.2802700Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/src/test/java/com/baomidou/mybatisplus/test/MybatisConfigurationTest.java:71: warning: [deprecation] isMultipleResultSetsEnabled() in Configuration has been deprecated
2026-06-29T04:03:53.2831749Z         Assertions.assertTrue(configuration.isMultipleResultSetsEnabled());
2026-06-29T04:03:53.2832807Z                                            ^
2026-06-29T04:03:53.2833862Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/src/test/java/com/baomidou/mybatisplus/test/MybatisConfigurationTest.java:131: warning: [deprecation] <T>addNewMapper(Class<T>) in MybatisConfiguration has been deprecated
2026-06-29T04:03:53.2834971Z         mybatisConfiguration.addNewMapper(BMapper.class);
2026-06-29T04:03:53.2835320Z                             ^
2026-06-29T04:03:53.2835575Z   where T is a type-variable:
2026-06-29T04:03:53.2835906Z     T extends Object declared in method <T>addNewMapper(Class<T>)
2026-06-29T04:03:53.3640521Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/src/test/java/com/baomidou/mybatisplus/test/MybatisConfigurationTest.java:132: warning: [deprecation] <T>addNewMapper(Class<T>) in MybatisConfiguration has been deprecated
2026-06-29T04:03:53.3791633Z         mybatisConfiguration.addNewMapper(AMapper.class);
2026-06-29T04:03:53.3844473Z                             ^
2026-06-29T04:03:53.3844824Z   where T is a type-variable:
2026-06-29T04:03:53.3845186Z     T extends Object declared in method <T>addNewMapper(Class<T>)
2026-06-29T04:03:53.3846246Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/src/test/java/com/baomidou/mybatisplus/test/toolkit/ReflectionKitTest.java:118: warning: [deprecation] getFieldValue(Object,String) in ReflectionKit has been deprecated
2026-06-29T04:03:53.3847389Z         Assertions.assertEquals(c.getSex(), ReflectionKit.getFieldValue(c, "sex"));
2026-06-29T04:03:53.3847864Z                                                          ^
2026-06-29T04:03:53.3854478Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/src/test/java/com/baomidou/mybatisplus/test/toolkit/ReflectionKitTest.java:119: warning: [deprecation] getFieldValue(Object,String) in ReflectionKit has been deprecated
2026-06-29T04:03:53.3886074Z         Assertions.assertEquals(c.getAge(), ReflectionKit.getFieldValue(c, "age"));
2026-06-29T04:03:53.3887129Z                                                          ^
2026-06-29T04:03:53.3889219Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/src/test/java/com/baomidou/mybatisplus/test/toolkit/ReflectionKitTest.java:124: warning: [deprecation] getFieldValue(Object,String) in ReflectionKit has been deprecated
2026-06-29T04:03:53.3891889Z         Assertions.assertEquals(entityByLombok.getPId(), ReflectionKit.getFieldValue(entityByLombok, "pId"));
2026-06-29T04:03:53.3893229Z                                                                       ^
2026-06-29T04:03:53.3895251Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/src/test/java/com/baomidou/mybatisplus/test/toolkit/ReflectionKitTest.java:125: warning: [deprecation] getFieldValue(Object,String) in ReflectionKit has been deprecated
2026-06-29T04:03:53.3898166Z         Assertions.assertEquals(entityByLombok.getParentId(), ReflectionKit.getFieldValue(entityByLombok, "parentId"));
2026-06-29T04:03:53.3899435Z                                                                            ^
2026-06-29T04:03:53.3901695Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/src/test/java/com/baomidou/mybatisplus/test/toolkit/ReflectionKitTest.java:130: warning: [deprecation] getFieldValue(Object,String) in ReflectionKit has been deprecated
2026-06-29T04:03:53.3904120Z         Assertions.assertEquals(entity.getParentId(), ReflectionKit.getFieldValue(entity, "parentId"));
2026-06-29T04:03:53.3905223Z                                                                    ^
2026-06-29T04:03:53.3907179Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/src/test/java/com/baomidou/mybatisplus/test/toolkit/ReflectionKitTest.java:131: warning: [deprecation] getFieldValue(Object,String) in ReflectionKit has been deprecated
2026-06-29T04:03:53.3909500Z         Assertions.assertEquals(entity.getpId(), ReflectionKit.getFieldValue(entity, "pId"));
2026-06-29T04:03:53.3971734Z                                                               ^
2026-06-29T04:03:53.6612486Z Note: Some input files use or override a deprecated API that is marked for removal.
2026-06-29T04:03:53.6661772Z Note: Recompile with -Xlint:removal for details.
2026-06-29T04:03:53.6714801Z 14 warnings
2026-06-29T04:03:56.6621444Z 
2026-06-29T04:03:56.6632067Z > Task :mybatis-plus-core:testClasses
2026-06-29T04:03:58.1608263Z > Task :mybatis-plus-extension:compileKotlin
2026-06-29T04:03:59.8607372Z OpenJDK 64-Bit Server VM warning: Sharing is only supported for boot loader classes because bootstrap classpath has been appended
2026-06-29T04:04:00.7631504Z 
2026-06-29T04:04:00.7642662Z > Task :mybatis-plus-core:test
2026-06-29T04:04:00.7670266Z 
2026-06-29T04:04:00.7682870Z MybatisConfigurationTest > testReload() FAILED
2026-06-29T04:04:00.7701574Z     org.opentest4j.AssertionFailedError at MybatisConfigurationTest.java:126
2026-06-29T04:04:01.2606970Z 
2026-06-29T04:04:01.2608776Z 165 tests completed, 1 failed, 23 skipped
2026-06-29T04:04:01.3621434Z 
2026-06-29T04:04:01.3621460Z 
2026-06-29T04:04:01.3647157Z FAILURE: Build failed with an exception.
2026-06-29T04:04:01.3647788Z > Task :mybatis-plus-core:test FAILED
2026-06-29T04:04:01.3648892Z > Task :mybatis-plus-generator:generateEffectiveLombokConfig
2026-06-29T04:04:01.3649688Z > Task :mybatis-plus-extension:generateTestEffectiveLombokConfig
2026-06-29T04:04:01.3649987Z 
2026-06-29T04:04:01.3650453Z [Incubating] Problems report is available at: file:///home/runner/work/mybatis-plus/mybatis-plus/build/reports/problems/problems-report.html
2026-06-29T04:04:01.3651489Z 
2026-06-29T04:04:01.3651930Z Deprecated Gradle features were used in this build, making it incompatible with Gradle 9.0.
2026-06-29T04:04:01.3652502Z 
2026-06-29T04:04:01.3653495Z You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.
2026-06-29T04:04:01.3654301Z 
2026-06-29T04:04:01.3655100Z For more on this, please refer to https://docs.gradle.org/8.13/userguide/command_line_interface.html#sec:command_line_warnings in the Gradle documentation.
2026-06-29T04:04:01.3656147Z 41 actionable tasks: 36 executed, 5 up-to-date
2026-06-29T04:04:01.3656378Z 
2026-06-29T04:04:01.3656468Z * What went wrong:
2026-06-29T04:04:01.3656740Z Execution failed for task ':mybatis-plus-core:test'.
2026-06-29T04:04:01.3657428Z > There were failing tests. See the report at: file:///home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus-core/build/reports/tests/test/index.html
2026-06-29T04:04:01.3657995Z 
2026-06-29T04:04:01.3658072Z * Try:
2026-06-29T04:04:01.3658279Z > Run with --scan to get full insights.
2026-06-29T04:04:01.3658721Z 
2026-06-29T04:04:01.3658855Z BUILD FAILED in 1m 12s
2026-06-29T04:04:01.7892703Z ##[error]Process completed with exit code 1.
2026-06-29T04:04:01.8040035Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-29T04:04:01.8041522Z Post job cleanup.
2026-06-29T04:04:01.9714518Z In post-action step
2026-06-29T04:04:01.9721330Z Cache is read-only: will not save state for use in subsequent builds.
2026-06-29T04:04:01.9723938Z (node:2719) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-06-29T04:04:01.9724948Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-06-29T04:04:01.9729771Z Generating Job Summary
2026-06-29T04:04:01.9765402Z Completed post-action step
2026-06-29T04:04:01.9944769Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-29T04:04:01.9946041Z Post job cleanup.
2026-06-29T04:04:02.1255397Z (node:2731) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-06-29T04:04:02.1358871Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-06-29T04:04:02.1429980Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-29T04:04:02.1431518Z Post job cleanup.
2026-06-29T04:04:02.2255761Z [command]/usr/bin/git version
2026-06-29T04:04:02.2293404Z git version 2.54.0
2026-06-29T04:04:02.2330523Z Temporarily overriding HOME='/home/runner/work/_temp/9682055a-33a5-431b-9158-d0d65a906b45' before making global git config changes
2026-06-29T04:04:02.2332282Z Adding repository directory to the temporary git global config as a safe directory
2026-06-29T04:04:02.2336010Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/mybatis-plus/mybatis-plus
2026-06-29T04:04:02.2371554Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-06-29T04:04:02.2406506Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-06-29T04:04:02.2669187Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-06-29T04:04:02.2699529Z http.https://github.com/.extraheader
2026-06-29T04:04:02.2711751Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-06-29T04:04:02.2745161Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-06-29T04:04:02.2989227Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-06-29T04:04:02.3022724Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-06-29T04:04:02.3398838Z Cleaning up orphan processes
2026-06-29T04:04:02.3693189Z Terminate orphan process: pid (2455) (java)
2026-06-29T04:04:02.3752252Z Terminate orphan process: pid (2607) (java)
2026-06-29T04:04:02.3789686Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/checkout@v4, actions/setup-java@v4, gradle/actions/setup-gradle@417ae3ccd767c252f5661f1ace9f835f9654f2b5. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 19. `baomidou__mybatis-plus__084235124274.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/baomidou__mybatis-plus__084235124274.txt` (authoritative; read this, not the excerpt)
- **Repository**: `baomidou/mybatis-plus`
- **Content hash (sha256, first 16)**: `29b095d8eba7ab0f`
- **Body size**: 64,315 bytes, 605 lines
- **Excerpt**: final 120 of 605 lines, content-blind

```text
2026-06-30T07:31:33.8480609Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus/src/test/java/com/baomidou/mybatisplus/test/toolkit/JdbcUtilsTest.java:31: warning: [deprecation] GAUSS in DbType has been deprecated
2026-06-30T07:31:33.8481969Z         Assertions.assertEquals(DbType.GAUSS, JdbcUtils.getDbType("jdbc:zenith://127.0.0.1:8000/baomidou"));
2026-06-30T07:31:33.8482488Z                                       ^
2026-06-30T07:31:34.1459708Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus/src/test/java/com/baomidou/mybatisplus/test/phoenix/PhoenixTest.java:52: warning: [deprecation] sqlSessionBatch(Class<?>) in SqlHelper has been deprecated
2026-06-30T07:31:34.1463899Z         try (SqlSession sqlSession = SqlHelper.sqlSessionBatch(PhoenixTestInfo.class)) {
2026-06-30T07:31:34.1465112Z                                               ^
2026-06-30T07:31:34.1466735Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus/src/test/java/com/baomidou/mybatisplus/test/phoenix/PhoenixTest.java:53: warning: [deprecation] getSqlStatement(String) in TableInfo has been deprecated
2026-06-30T07:31:34.1468723Z             String sqlStatement = SqlHelper.table(PhoenixTestInfo.class).getSqlStatement(UPSERT_ONE.getMethod());
2026-06-30T07:31:34.1469777Z                                                                         ^
2026-06-30T07:31:34.1471927Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus/src/test/java/com/baomidou/mybatisplus/test/logicdel/LogicDelTest.java:134: warning: [deprecation] LogicDeleteBatchByIds in com.baomidou.mybatisplus.extension.injector.methods has been deprecated
2026-06-30T07:31:34.1473860Z                 methodList.add(new LogicDeleteBatchByIds("testDeleteBatch"));
2026-06-30T07:31:34.1474889Z                                    ^
2026-06-30T07:31:34.3485469Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus/src/test/java/com/baomidou/mybatisplus/test/h2/customfill/CustomFillConfig.java:72: warning: [deprecation] getConfiguration() in TableInfo has been deprecated
2026-06-30T07:31:34.3533763Z                         AnnotationHandler annotationHandler = GlobalConfigUtils.getGlobalConfig(TableInfoHelper.getTableInfo(clazz).getConfiguration()).getAnnotationHandler();
2026-06-30T07:31:34.3590396Z                                                                                                                                    ^
2026-06-30T07:31:34.3603957Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus/src/test/java/com/baomidou/mybatisplus/test/h2/config/MybatisPlusConfig.java:59: warning: [deprecation] DataChangeRecorderInnerInterceptor in com.baomidou.mybatisplus.extension.plugins.inner has been deprecated
2026-06-30T07:31:34.3629019Z         mybatisPlusInterceptor.addInnerInterceptor(new DataChangeRecorderInnerInterceptor());
2026-06-30T07:31:34.3654231Z                                                        ^
2026-06-30T07:31:34.3693671Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus/src/test/java/com/baomidou/mybatisplus/test/h2/config/MybatisPlusConfigLogicDelete.java:70: warning: [deprecation] LogicDeleteByIdWithFill in com.baomidou.mybatisplus.extension.injector.methods has been deprecated
2026-06-30T07:31:34.3722153Z                 methodList.add(new LogicDeleteByIdWithFill());
2026-06-30T07:31:34.3722866Z                                    ^
2026-06-30T07:31:34.3753563Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus/src/test/java/com/baomidou/mybatisplus/test/h2/H2UserTest.java:82: warning: [deprecation] DataChangeRecorderInnerInterceptor in com.baomidou.mybatisplus.extension.plugins.inner has been deprecated
2026-06-30T07:31:34.3782340Z                         if (innerInterceptor instanceof DataChangeRecorderInnerInterceptor) {
2026-06-30T07:31:34.3812097Z                                                         ^
2026-06-30T07:31:34.3814106Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus/src/test/java/com/baomidou/mybatisplus/test/h2/H2UserTest.java:83: warning: [deprecation] DataChangeRecorderInnerInterceptor in com.baomidou.mybatisplus.extension.plugins.inner has been deprecated
2026-06-30T07:31:34.3842697Z                             ((DataChangeRecorderInnerInterceptor) innerInterceptor).setBatchUpdateLimit(limitation).openBatchUpdateLimitation();
2026-06-30T07:31:34.3872112Z                               ^
2026-06-30T07:31:34.3903436Z /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus/src/test/java/com/baomidou/mybatisplus/test/h2/H2UserTest.java:297: warning: [deprecation] DataChangeRecorderInnerInterceptor in com.baomidou.mybatisplus.extension.plugins.inner has been deprecated
2026-06-30T07:31:34.3906396Z         if (e instanceof DataChangeRecorderInnerInterceptor.DataUpdateLimitationException) {
2026-06-30T07:31:34.3932197Z                          ^
2026-06-30T07:31:34.8458916Z Note: /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus/src/test/java/com/baomidou/mybatisplus/test/PageTest.java uses or overrides a deprecated API that is marked for removal.
2026-06-30T07:31:34.8482469Z Note: Recompile with -Xlint:removal for details.
2026-06-30T07:31:34.8513055Z Note: /home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus/src/test/java/com/baomidou/mybatisplus/test/h2/customfill/CustomFillConfig.java uses unchecked or unsafe operations.
2026-06-30T07:31:34.8542235Z Note: Recompile with -Xlint:unchecked for details.
2026-06-30T07:31:34.8542961Z 12 warnings
2026-06-30T07:31:35.3459069Z 
2026-06-30T07:31:35.3459899Z > Task :mybatis-plus:testClasses
2026-06-30T07:31:39.6458701Z OpenJDK 64-Bit Server VM warning: Sharing is only supported for boot loader classes because bootstrap classpath has been appended
2026-06-30T07:31:40.8458046Z 
2026-06-30T07:31:40.8459052Z > Task :mybatis-plus:test
2026-06-30T07:31:40.8459615Z 
2026-06-30T07:31:40.8459981Z AutoResultMapTest > test() FAILED
2026-06-30T07:31:40.8460716Z     java.lang.AssertionError at AutoResultMapTest.java:24
2026-06-30T07:31:50.5462466Z 
2026-06-30T07:31:50.5512706Z ResultMapTest > test() FAILED
2026-06-30T07:31:50.5513287Z     java.lang.AssertionError at ResultMapTest.java:30
2026-06-30T07:31:52.8457946Z 
2026-06-30T07:31:52.8459468Z 07:31:52.806 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@632a7680, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8461610Z 07:31:52.806 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@780e6b63, started on Tue Jun 30 07:31:50 UTC 2026
2026-06-30T07:31:52.8463353Z 07:31:52.807 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@7ae49d52, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8464729Z 07:31:52.808 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@75cfb958, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8466097Z 07:31:52.808 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@19266ca3, started on Tue Jun 30 07:31:50 UTC 2026
2026-06-30T07:31:52.8467417Z 07:31:52.808 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@5dff108c, started on Tue Jun 30 07:31:43 UTC 2026
2026-06-30T07:31:52.8468728Z 07:31:52.810 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@77e2a5d3, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8470045Z 07:31:52.810 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@217abcc9, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8471367Z 07:31:52.810 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@c9518ee, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8473444Z 07:31:52.810 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@41fbe8c0, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8475484Z 07:31:52.811 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@15549dd7, started on Tue Jun 30 07:31:42 UTC 2026
2026-06-30T07:31:52.8477517Z 07:31:52.812 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@331fe6d4, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8479874Z 07:31:52.812 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@62243a7a, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8481547Z 07:31:52.814 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@75c2a35, started on Tue Jun 30 07:31:52 UTC 2026
2026-06-30T07:31:52.8483210Z 07:31:52.814 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@746da54f, started on Tue Jun 30 07:31:42 UTC 2026
2026-06-30T07:31:52.9473109Z 
2026-06-30T07:31:52.9473135Z 
2026-06-30T07:31:52.9512595Z 1239 tests completed, 2 failed, 1 skipped
2026-06-30T07:31:52.9513167Z > Task :mybatis-plus:test
2026-06-30T07:31:53.4465145Z 
2026-06-30T07:31:53.4483719Z > Task :mybatis-plus:test FAILED
2026-06-30T07:31:53.4484513Z 
2026-06-30T07:31:53.4485401Z [Incubating] Problems report is available at: file:///home/runner/work/mybatis-plus/mybatis-plus/build/reports/problems/problems-report.html
2026-06-30T07:31:53.5457104Z 
2026-06-30T07:31:53.5472124Z 
2026-06-30T07:31:53.5483196Z FAILURE: Build failed with an exception.
2026-06-30T07:31:53.5484014Z Deprecated Gradle features were used in this build, making it incompatible with Gradle 9.0.
2026-06-30T07:31:53.5496608Z 
2026-06-30T07:31:53.5522300Z * What went wrong:
2026-06-30T07:31:53.5522532Z 
2026-06-30T07:31:53.5548280Z Execution failed for task ':mybatis-plus:test'.
2026-06-30T07:31:53.5549340Z You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.
2026-06-30T07:31:53.5552889Z > There were failing tests. See the report at: file:///home/runner/work/mybatis-plus/mybatis-plus/mybatis-plus/build/reports/tests/test/index.html
2026-06-30T07:31:53.5553729Z 
2026-06-30T07:31:53.5554451Z For more on this, please refer to https://docs.gradle.org/8.13/userguide/command_line_interface.html#sec:command_line_warnings in the Gradle documentation.
2026-06-30T07:31:53.5555256Z 
2026-06-30T07:31:53.5555378Z * Try:
2026-06-30T07:31:53.5555675Z > Run with --scan to get full insights.
2026-06-30T07:31:53.5555949Z 
2026-06-30T07:31:53.5556077Z BUILD FAILED in 1m 43s
2026-06-30T07:31:53.5556428Z 55 actionable tasks: 50 executed, 5 up-to-date
2026-06-30T07:31:53.8784836Z ##[error]Process completed with exit code 1.
2026-06-30T07:31:53.8940281Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-30T07:31:53.8943228Z Post job cleanup.
2026-06-30T07:31:54.0610840Z In post-action step
2026-06-30T07:31:54.0617380Z Cache is read-only: will not save state for use in subsequent builds.
2026-06-30T07:31:54.0620156Z (node:2768) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-06-30T07:31:54.0621032Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-06-30T07:31:54.0626010Z Generating Job Summary
2026-06-30T07:31:54.0662659Z Completed post-action step
2026-06-30T07:31:54.0834575Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-30T07:31:54.0835742Z Post job cleanup.
2026-06-30T07:31:54.2162469Z (node:2780) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-06-30T07:31:54.2163651Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-06-30T07:31:54.2400296Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-30T07:31:54.2401480Z Post job cleanup.
2026-06-30T07:31:54.3259690Z [command]/usr/bin/git version
2026-06-30T07:31:54.3296719Z git version 2.54.0
2026-06-30T07:31:54.3331311Z Temporarily overriding HOME='/home/runner/work/_temp/a13cc907-689f-4340-8f3f-f66660e8bae1' before making global git config changes
2026-06-30T07:31:54.3332616Z Adding repository directory to the temporary git global config as a safe directory
2026-06-30T07:31:54.3336820Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/mybatis-plus/mybatis-plus
2026-06-30T07:31:54.3374414Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-06-30T07:31:54.3409414Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-06-30T07:31:54.3682547Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-06-30T07:31:54.3707045Z http.https://github.com/.extraheader
2026-06-30T07:31:54.3718172Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-06-30T07:31:54.3750447Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-06-30T07:31:54.3980502Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-06-30T07:31:54.4012074Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-06-30T07:31:54.4396193Z Cleaning up orphan processes
2026-06-30T07:31:54.4709551Z Terminate orphan process: pid (2387) (java)
2026-06-30T07:31:54.4747512Z Terminate orphan process: pid (2537) (java)
2026-06-30T07:31:54.4757700Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/checkout@v4, actions/setup-java@v4, gradle/actions/setup-gradle@417ae3ccd767c252f5661f1ace9f835f9654f2b5. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 20. `dask__distributed__084757050312.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/dask__distributed__084757050312.txt` (authoritative; read this, not the excerpt)
- **Repository**: `dask/distributed`
- **Content hash (sha256, first 16)**: `de3a23f971790d6f`
- **Body size**: 513,446 bytes, 4,420 lines
- **Excerpt**: final 120 of 4,420 lines, content-blind

```text
2026-07-02T11:18:04.2751112Z 
2026-07-02T11:18:04.5022941Z   0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
2026-07-02T11:18:04.5023380Z 100 10.4M  100 10.4M    0     0  45.8M      0 --:--:-- --:--:-- --:--:-- 45.8M
2026-07-02T11:18:04.5041351Z [0;32m==>[0m Finishing downloading [0;36mlinux-arm64:latest[0m
2026-07-02T11:18:04.5868225Z       Version: [0;36mv11.0.3[0m
2026-07-02T11:18:04.5868523Z  
2026-07-02T11:18:04.6489836Z gpg: directory '/home/runner/.gnupg' created
2026-07-02T11:18:04.6490964Z gpg: keybox '/home/runner/.gnupg/pubring.kbx' created
2026-07-02T11:18:04.7431053Z gpg: /home/runner/.gnupg/trustdb.gpg: trustdb created
2026-07-02T11:18:04.7431655Z gpg: key 806BB28AED779869: public key "Codecov Uploader (Codecov Uploader Verification Key) <security@codecov.io>" imported
2026-07-02T11:18:04.7751530Z gpg: Total number processed: 1
2026-07-02T11:18:04.7751835Z gpg:               imported: 1
2026-07-02T11:18:04.7754907Z [0;32m==>[0m Verifying GPG signature integrity
2026-07-02T11:18:04.7755639Z [0;32m ->[0m Downloading [0;36mhttps://cli.codecov.io/latest/linux-arm64/codecov.SHA256SUM[0m
2026-07-02T11:18:04.7756597Z [0;32m ->[0m Downloading [0;36mhttps://cli.codecov.io/latest/linux-arm64/codecov.SHA256SUM.sig[0m
2026-07-02T11:18:04.7757137Z  
2026-07-02T11:18:04.9679419Z gpg: Signature made Thu May 29 21:23:36 2025 UTC
2026-07-02T11:18:04.9680309Z gpg:                using RSA key 27034E7FDB850E0BBC2C62FF806BB28AED779869
2026-07-02T11:18:04.9680930Z gpg: Good signature from "Codecov Uploader (Codecov Uploader Verification Key) <security@codecov.io>" [unknown]
2026-07-02T11:18:04.9681496Z gpg: WARNING: This key is not certified with a trusted signature!
2026-07-02T11:18:04.9681907Z gpg:          There is no indication that the signature belongs to the owner.
2026-07-02T11:18:04.9682348Z Primary key fingerprint: 2703 4E7F DB85 0E0B BC2C  62FF 806B B28A ED77 9869
2026-07-02T11:18:05.0340093Z codecov: OK
2026-07-02T11:18:05.0346682Z [0;32m==>[0m CLI integrity verified
2026-07-02T11:18:05.0346886Z 
2026-07-02T11:18:05.1048982Z [0;32m ->[0m Token length: 0
2026-07-02T11:18:05.1049358Z [0;32m==>[0m Running upload-coverage
2026-07-02T11:18:05.1059753Z       [0;36m./codecov  upload-coverage --git-service github --pr 9313 --sha dfc33a7fe93c9a090fe26bb92703ebe2f54c3571 --branch crusaderky:test_failure_during_worker_initialization --gcov-executable gcov --name ubuntu-24.04-arm-py310-test-ci-ci1[0m
2026-07-02T11:18:05.3785931Z info - 2026-07-02 11:18:05,378 -- ci service found: github-actions
2026-07-02T11:18:05.4147950Z warning - 2026-07-02 11:18:05,414 -- xcrun is not installed or can't be found.
2026-07-02T11:18:06.7135081Z warning - 2026-07-02 11:18:06,713 -- No gcov data found.
2026-07-02T11:18:06.7137868Z warning - 2026-07-02 11:18:06,713 -- coverage.py is not installed or can't be found.
2026-07-02T11:18:06.9264331Z info - 2026-07-02 11:18:06,925 -- Found 1 coverage files to report
2026-07-02T11:18:06.9264829Z info - 2026-07-02 11:18:06,926 -- > /home/runner/work/distributed/distributed/coverage.xml
2026-07-02T11:18:07.2960200Z info - 2026-07-02 11:18:07,295 -- Your upload is now processing. When finished, results will be available at: https://app.codecov.io/github/dask/distributed/commit/dfc33a7fe93c9a090fe26bb92703ebe2f54c3571
2026-07-02T11:18:07.5911115Z info - 2026-07-02 11:18:07,590 -- Process Upload complete
2026-07-02T11:18:07.7821406Z ##[group]Run actions/upload-artifact@v7
2026-07-02T11:18:07.7821701Z with:
2026-07-02T11:18:07.7821892Z   name: ubuntu-24.04-arm-py310-test-ci-ci1
2026-07-02T11:18:07.7822143Z   path: pytest.xml
2026-07-02T11:18:07.7822334Z   if-no-files-found: warn
2026-07-02T11:18:07.7822647Z   compression-level: 6
2026-07-02T11:18:07.7822843Z   overwrite: false
2026-07-02T11:18:07.7823032Z   include-hidden-files: false
2026-07-02T11:18:07.7823250Z   archive: true
2026-07-02T11:18:07.7823419Z env:
2026-07-02T11:18:07.7823603Z   TEST_ID: ubuntu-24.04-arm-py310-test-ci-ci1
2026-07-02T11:18:07.7823858Z   DISABLE_IPV6: 1
2026-07-02T11:18:07.7824036Z   CC_FORK: true
2026-07-02T11:18:07.7824301Z   TOKENLESS: crusaderky:test_failure_during_worker_initialization
2026-07-02T11:18:07.7824699Z   CC_BRANCH: crusaderky:test_failure_during_worker_initialization
2026-07-02T11:18:07.7825048Z   CC_SHA: dfc33a7fe93c9a090fe26bb92703ebe2f54c3571
2026-07-02T11:18:07.7825331Z   CC_PR: 9313
2026-07-02T11:18:07.7825528Z ##[endgroup]
2026-07-02T11:18:07.8999762Z With the provided path, there will be 1 file uploaded
2026-07-02T11:18:07.9004032Z Artifact name is valid!
2026-07-02T11:18:07.9004409Z Root directory input is valid!
2026-07-02T11:18:08.1984527Z Uploading artifact: ubuntu-24.04-arm-py310-test-ci-ci1.zip
2026-07-02T11:18:08.2019399Z Beginning upload of artifact content to blob storage
2026-07-02T11:18:08.3612179Z Uploaded bytes 2179
2026-07-02T11:18:08.4002830Z Finished uploading artifact content to blob storage!
2026-07-02T11:18:08.4003519Z SHA256 digest of uploaded artifact is 862e0f1bfeadfdb1dbbc629c6b0701c40fd27aea392c8946f21661052052c3a5
2026-07-02T11:18:08.4004009Z Finalizing artifact upload
2026-07-02T11:18:08.6592200Z Artifact ubuntu-24.04-arm-py310-test-ci-ci1 successfully finalized. Artifact ID 8037052029
2026-07-02T11:18:08.6592952Z Artifact ubuntu-24.04-arm-py310-test-ci-ci1 has been successfully uploaded! Final size is 2179 bytes. Artifact ID is 8037052029
2026-07-02T11:18:08.6596429Z Artifact download URL: https://github.com/dask/distributed/actions/runs/28585825385/artifacts/8037052029
2026-07-02T11:18:08.6715379Z ##[group]Run actions/upload-artifact@v7
2026-07-02T11:18:08.6715935Z with:
2026-07-02T11:18:08.6716202Z   name: ubuntu-24.04-arm-py310-test-ci-ci1_cluster_dumps
2026-07-02T11:18:08.6716890Z   path: test_cluster_dump
2026-07-02T11:18:08.6717243Z   if-no-files-found: ignore
2026-07-02T11:18:08.6717474Z   compression-level: 6
2026-07-02T11:18:08.6717675Z   overwrite: false
2026-07-02T11:18:08.6717875Z   include-hidden-files: false
2026-07-02T11:18:08.6718097Z   archive: true
2026-07-02T11:18:08.6718273Z env:
2026-07-02T11:18:08.6718464Z   TEST_ID: ubuntu-24.04-arm-py310-test-ci-ci1
2026-07-02T11:18:08.6718729Z   DISABLE_IPV6: 1
2026-07-02T11:18:08.6719080Z   CC_FORK: true
2026-07-02T11:18:08.6719560Z   TOKENLESS: crusaderky:test_failure_during_worker_initialization
2026-07-02T11:18:08.6719992Z   CC_BRANCH: crusaderky:test_failure_during_worker_initialization
2026-07-02T11:18:08.6720656Z   CC_SHA: dfc33a7fe93c9a090fe26bb92703ebe2f54c3571
2026-07-02T11:18:08.6720924Z   CC_PR: 9313
2026-07-02T11:18:08.6721130Z ##[endgroup]
2026-07-02T11:18:08.7891678Z No files were found with the provided path: test_cluster_dump. No artifacts will be uploaded.
2026-07-02T11:18:08.8041198Z Post job cleanup.
2026-07-02T11:18:08.8870274Z Post job cleanup.
2026-07-02T11:18:08.9584412Z [command]/usr/bin/git version
2026-07-02T11:18:08.9620947Z git version 2.54.0
2026-07-02T11:18:08.9647140Z Copying '/home/runner/.gitconfig' to '/home/runner/work/_temp/14b52b1b-7c10-4f23-b6fe-e4a000e7da61/.gitconfig'
2026-07-02T11:18:09.0144979Z Temporarily overriding HOME='/home/runner/work/_temp/14b52b1b-7c10-4f23-b6fe-e4a000e7da61' before making global git config changes
2026-07-02T11:18:09.0145966Z Adding repository directory to the temporary git global config as a safe directory
2026-07-02T11:18:09.0161329Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/distributed/distributed
2026-07-02T11:18:09.0201059Z Removing SSH command configuration
2026-07-02T11:18:09.0207939Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-07-02T11:18:09.0237479Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-07-02T11:18:09.0438141Z Removing HTTP extra header
2026-07-02T11:18:09.0443661Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-02T11:18:09.0479359Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-07-02T11:18:09.0684134Z Removing includeIf entries pointing to credentials config files
2026-07-02T11:18:09.0692115Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-02T11:18:09.0719810Z includeif.gitdir:/home/runner/work/distributed/distributed/.git.path
2026-07-02T11:18:09.0720441Z includeif.gitdir:/home/runner/work/distributed/distributed/.git/worktrees/*.path
2026-07-02T11:18:09.0720956Z includeif.gitdir:/github/workspace/.git.path
2026-07-02T11:18:09.0721398Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-02T11:18:09.0729118Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/distributed/distributed/.git.path
2026-07-02T11:18:09.0752036Z /home/runner/work/_temp/git-credentials-5391e2e4-8c93-4d05-9d34-40edfdf292fd.config
2026-07-02T11:18:09.0761080Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/distributed/distributed/.git.path /home/runner/work/_temp/git-credentials-5391e2e4-8c93-4d05-9d34-40edfdf292fd.config
2026-07-02T11:18:09.1105755Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/distributed/distributed/.git/worktrees/*.path
2026-07-02T11:18:09.1133545Z /home/runner/work/_temp/git-credentials-5391e2e4-8c93-4d05-9d34-40edfdf292fd.config
2026-07-02T11:18:09.1145158Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/distributed/distributed/.git/worktrees/*.path /home/runner/work/_temp/git-credentials-5391e2e4-8c93-4d05-9d34-40edfdf292fd.config
2026-07-02T11:18:09.1181690Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-07-02T11:18:09.1212546Z /github/runner_temp/git-credentials-5391e2e4-8c93-4d05-9d34-40edfdf292fd.config
2026-07-02T11:18:09.1219450Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git.path /github/runner_temp/git-credentials-5391e2e4-8c93-4d05-9d34-40edfdf292fd.config
2026-07-02T11:18:09.1577408Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-02T11:18:09.1603226Z /github/runner_temp/git-credentials-5391e2e4-8c93-4d05-9d34-40edfdf292fd.config
2026-07-02T11:18:09.1611165Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path /github/runner_temp/git-credentials-5391e2e4-8c93-4d05-9d34-40edfdf292fd.config
2026-07-02T11:18:09.1645706Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-07-02T11:18:09.1833946Z Removing credentials config '/home/runner/work/_temp/git-credentials-5391e2e4-8c93-4d05-9d34-40edfdf292fd.config'
2026-07-02T11:18:09.1962060Z Cleaning up orphan processes
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 21. `diffplug__spotless__080436519238.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/diffplug__spotless__080436519238.txt` (authoritative; read this, not the excerpt)
- **Repository**: `diffplug/spotless`
- **Content hash (sha256, first 16)**: `da4a323e35ca1b10`
- **Body size**: 501,429 bytes, 6,511 lines
- **Excerpt**: final 120 of 6,511 lines, content-blind

```text
2026-06-09T22:19:17.9210980Z 
2026-06-09T22:19:17.9211072Z * What went wrong:
2026-06-09T22:19:17.9211340Z Execution failed for task ':plugin-gradle:test'.
2026-06-09T22:19:17.9211926Z > There were failing tests. See the report at: file:///D:/a/spotless/spotless/plugin-gradle/build/reports/tests/test/index.html
2026-06-09T22:19:17.9212379Z 
2026-06-09T22:19:17.9212479Z BUILD FAILED in 19m 25s
2026-06-09T22:19:18.1189332Z 
2026-06-09T22:19:18.1190136Z Publishing Build Scan to Develocity...
2026-06-09T22:19:18.5138049Z gradle/actions: Writing build results to D:\a\_temp\.gradle-actions\build-scans\__run_2-1781042415115.json
2026-06-09T22:19:18.7199385Z https://gradle.com/s/nuneiyojuy6rk
2026-06-09T22:19:18.7199744Z 
2026-06-09T22:19:18.7199851Z Configuration cache entry stored.
2026-06-09T22:19:30.8484287Z ##[error]Process completed with exit code 1.
2026-06-09T22:19:31.9517822Z ##[group]Run mikepenz/action-junit-report@v6
2026-06-09T22:19:31.9518194Z with:
2026-06-09T22:19:31.9518371Z   check_name: JUnit gradle 17 windows-latest
2026-06-09T22:19:31.9518597Z   report_paths: */build/test-results/*/TEST-*.xml
2026-06-09T22:19:31.9518796Z   check_retries: true
2026-06-09T22:19:31.9520661Z   token: ***
2026-06-09T22:19:31.9520803Z   group_reports: true
2026-06-09T22:19:31.9520964Z   annotate_only: false
2026-06-09T22:19:31.9521118Z   check_annotations: true
2026-06-09T22:19:31.9521283Z   update_check: false
2026-06-09T22:19:31.9521431Z   fail_on_failure: false
2026-06-09T22:19:31.9521590Z   fail_on_parse_error: false
2026-06-09T22:19:31.9521791Z   require_tests: false
2026-06-09T22:19:31.9521946Z   require_passed_tests: false
2026-06-09T22:19:31.9522109Z   include_passed: false
2026-06-09T22:19:31.9522297Z   include_skipped: true
2026-06-09T22:19:31.9522454Z   bread_crumb_delimiter: /
2026-06-09T22:19:31.9522616Z   transformers: []
2026-06-09T22:19:31.9522789Z   job_summary: true
2026-06-09T22:19:31.9522938Z   detailed_summary: false
2026-06-09T22:19:31.9523089Z   flaky_summary: false
2026-06-09T22:19:31.9523240Z   verbose_summary: true
2026-06-09T22:19:31.9523398Z   skip_success_summary: false
2026-06-09T22:19:31.9523567Z   include_empty_in_summary: true
2026-06-09T22:19:31.9523736Z   include_time_in_summary: false
2026-06-09T22:19:31.9523910Z   simplified_summary: false
2026-06-09T22:19:31.9524071Z   group_suite: false
2026-06-09T22:19:31.9524213Z   comment: false
2026-06-09T22:19:31.9565631Z   updateComment: true
2026-06-09T22:19:31.9565860Z   annotate_notice: false
2026-06-09T22:19:31.9566299Z   follow_symlink: false
2026-06-09T22:19:31.9566451Z   job_name: build
2026-06-09T22:19:31.9566593Z   truncate_stack_traces: true
2026-06-09T22:19:31.9566770Z   resolve_ignore_classname: false
2026-06-09T22:19:31.9566955Z   skip_comment_without_tests: false
2026-06-09T22:19:31.9567126Z env:
2026-06-09T22:19:31.9567350Z   JAVA_HOME: C:\hostedtoolcache\windows\Java_Temurin-Hotspot_jdk\17.0.19-10\x64
2026-06-09T22:19:31.9567687Z   JAVA_HOME_17_X64: C:\hostedtoolcache\windows\Java_Temurin-Hotspot_jdk\17.0.19-10\x64
2026-06-09T22:19:31.9567961Z   GRADLE_ACTION_ID: gradle/actions/setup-gradle
2026-06-09T22:19:31.9568157Z   GRADLE_USER_HOME: D:\a\.gradle
2026-06-09T22:19:31.9568341Z   GRADLE_BUILD_ACTION_SETUP_COMPLETED: true
2026-06-09T22:19:31.9568532Z   GRADLE_BUILD_ACTION_CACHE_RESTORED: true
2026-06-09T22:19:31.9568809Z   DEVELOCITY_INJECTION_INIT_SCRIPT_NAME: gradle-actions.inject-develocity.init.gradle
2026-06-09T22:19:31.9569106Z   DEVELOCITY_INJECTION_CUSTOM_VALUE: gradle-actions
2026-06-09T22:19:31.9569312Z   GITHUB_DEPENDENCY_GRAPH_ENABLED: false
2026-06-09T22:19:31.9569487Z ##[endgroup]
2026-06-09T22:19:32.1519540Z ##[group]📘 Reading input values
2026-06-09T22:19:32.1520454Z ##[endgroup]
2026-06-09T22:19:32.1635199Z ##[group]📦 Process test results
2026-06-09T22:19:32.1635595Z Preparing 1 report as configured.
2026-06-09T22:19:32.8344006Z plugin-gradle\src\test\java\com\diffplug\gradle\spotless\LicenseHeaderTest.java:96 | org.gradle.testkit.runner.UnexpectedBuildFailure: Unexpected build execution failure in C:\Users\runneradmin\AppData\Local\Temp\junit-2645742239775413316 with arguments [spotlessApply, --stacktrace]
2026-06-09T22:19:32.8344958Z  1.062s
2026-06-09T22:19:32.8460445Z ℹ️ Posting with conclusion 'failure' to https://github.com/diffplug/spotless/pull/2965 (sha: cb4bb9e1be85fef991a241992978c9b9ff45f381)
2026-06-09T22:19:32.8460945Z ##[endgroup]
2026-06-09T22:19:32.8461256Z ##[group]🚀 Publish results
2026-06-09T22:19:32.8636632Z ℹ️ - JUnit gradle 17 windows-latest - 663 tests run, 654 passed, 8 skipped, 1 failed.
2026-06-09T22:19:32.8639128Z    🧪 - plugin-gradle\src\test\java\com\diffplug\gradle\spotless\LicenseHeaderTest.java | org.gradle.testkit.runner.UnexpectedBuildFailure: Unexpected build execution failure in C:\Users\runneradmin\AppData\Local\Temp\junit-2645742239775413316 with arguments [spotlessApply, --stacktrace]
2026-06-09T22:19:32.8639739Z 
2026-06-09T22:19:33.2755202Z ℹ️ - JUnit gradle 17 windows-latest - Creating check (Annotations: 1)
2026-06-09T22:19:33.4106505Z ##[error]❌ Failed to create checks using the provided token. (HttpError: Resource not accessible by integration - https://docs.github.com/rest/checks/runs#create-a-check-run)
2026-06-09T22:19:33.4108925Z ##[warning]⚠️ This usually indicates insufficient permissions. More details: https://github.com/mikepenz/action-junit-report/issues/23
2026-06-09T22:19:33.4109630Z ##[endgroup]
2026-06-09T22:19:33.4542348Z Post job cleanup.
2026-06-09T22:19:33.7500593Z In post-action step
2026-06-09T22:19:33.7508241Z Cache is read-only: will not save state for use in subsequent builds.
2026-06-09T22:19:33.7513272Z Generating Job Summary
2026-06-09T22:19:33.7537598Z Completed post-action step
2026-06-09T22:19:33.7862775Z Post job cleanup.
2026-06-09T22:19:33.9300567Z Post job cleanup.
2026-06-09T22:19:34.0502466Z [command]"C:\Program Files\Git\bin\git.exe" version
2026-06-09T22:19:34.0706920Z git version 2.54.0.windows.1
2026-06-09T22:19:34.0757482Z Temporarily overriding HOME='D:\a\_temp\676ec9d5-9e88-4ce3-971d-fd7a4b356fbb' before making global git config changes
2026-06-09T22:19:34.0758104Z Adding repository directory to the temporary git global config as a safe directory
2026-06-09T22:19:34.0764959Z [command]"C:\Program Files\Git\bin\git.exe" config --global --add safe.directory D:\a\spotless\spotless
2026-06-09T22:19:34.1254280Z Removing SSH command configuration
2026-06-09T22:19:34.1263779Z [command]"C:\Program Files\Git\bin\git.exe" config --local --name-only --get-regexp core\.sshCommand
2026-06-09T22:19:34.2217186Z [command]"C:\Program Files\Git\bin\git.exe" submodule foreach --recursive "sh -c \"git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :\""
2026-06-09T22:19:35.7265105Z Removing HTTP extra header
2026-06-09T22:19:35.7278844Z [command]"C:\Program Files\Git\bin\git.exe" config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-06-09T22:19:35.7507371Z [command]"C:\Program Files\Git\bin\git.exe" submodule foreach --recursive "sh -c \"git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :\""
2026-06-09T22:19:36.1964062Z Removing includeIf entries pointing to credentials config files
2026-06-09T22:19:36.1973900Z [command]"C:\Program Files\Git\bin\git.exe" config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-06-09T22:19:36.2181013Z includeif.gitdir:D:/a/spotless/spotless/.git.path
2026-06-09T22:19:36.2181380Z includeif.gitdir:D:/a/spotless/spotless/.git/worktrees/*.path
2026-06-09T22:19:36.2181626Z includeif.gitdir:/github/workspace/.git.path
2026-06-09T22:19:36.2181874Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-06-09T22:19:36.2215665Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all includeif.gitdir:D:/a/spotless/spotless/.git.path
2026-06-09T22:19:36.2393954Z D:\a\_temp\git-credentials-887c4a58-aef5-475a-ae37-bcbf456cba52.config
2026-06-09T22:19:36.2426369Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset includeif.gitdir:D:/a/spotless/spotless/.git.path D:\a\_temp\git-credentials-887c4a58-aef5-475a-ae37-bcbf456cba52.config
2026-06-09T22:19:36.2626230Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all includeif.gitdir:D:/a/spotless/spotless/.git/worktrees/*.path
2026-06-09T22:19:36.2794670Z D:\a\_temp\git-credentials-887c4a58-aef5-475a-ae37-bcbf456cba52.config
2026-06-09T22:19:36.2831048Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset includeif.gitdir:D:/a/spotless/spotless/.git/worktrees/*.path D:\a\_temp\git-credentials-887c4a58-aef5-475a-ae37-bcbf456cba52.config
2026-06-09T22:19:36.3065851Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-06-09T22:19:36.3261458Z /github/runner_temp/git-credentials-887c4a58-aef5-475a-ae37-bcbf456cba52.config
2026-06-09T22:19:36.3294404Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset includeif.gitdir:/github/workspace/.git.path /github/runner_temp/git-credentials-887c4a58-aef5-475a-ae37-bcbf456cba52.config
2026-06-09T22:19:36.3509105Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-06-09T22:19:36.3688209Z /github/runner_temp/git-credentials-887c4a58-aef5-475a-ae37-bcbf456cba52.config
2026-06-09T22:19:36.3725106Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path /github/runner_temp/git-credentials-887c4a58-aef5-475a-ae37-bcbf456cba52.config
2026-06-09T22:19:36.3977236Z [command]"C:\Program Files\Git\bin\git.exe" submodule foreach --recursive "git config --local --show-origin --name-only --get-regexp remote.origin.url"
2026-06-09T22:19:36.8142508Z Removing credentials config 'D:\a\_temp\git-credentials-887c4a58-aef5-475a-ae37-bcbf456cba52.config'
2026-06-09T22:19:36.8357685Z Cleaning up orphan processes
2026-06-09T22:19:36.8855924Z Terminate orphan process: pid (1236) (java)
2026-06-09T22:19:37.1756755Z Terminate orphan process: pid (2276) (java)
2026-06-09T22:19:37.1840699Z Terminate orphan process: pid (8816) (conhost)
2026-06-09T22:19:37.5959824Z Terminate orphan process: pid (1312) (java)
2026-06-09T22:19:37.8155995Z Terminate orphan process: pid (7088) (java)
2026-06-09T22:19:38.0606271Z Terminate orphan process: pid (8744) (conhost)
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 22. `diffplug__spotless__095081359640.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/diffplug__spotless__095081359640.txt` (authoritative; read this, not the excerpt)
- **Repository**: `diffplug/spotless`
- **Content hash (sha256, first 16)**: `e16e3fde6c1b38e3`
- **Body size**: 102,438 bytes, 952 lines
- **Excerpt**: final 120 of 952 lines, content-blind

```text
2026-08-15T23:02:37.5645746Z ---
2026-08-15T23:02:37.5646161Z Entry: caches\9.4.1\generated-gradle-jars\gradle-test-kit-9.4.1.jar
2026-08-15T23:02:37.5646909Z     Requested Key : gradle-generated-gradle-jars-v2-b1c8c91f1defd0ba6d2b2ac7f0e028ec
2026-08-15T23:02:37.5647823Z     Restored  Key : gradle-generated-gradle-jars-v2-b1c8c91f1defd0ba6d2b2ac7f0e028ec
2026-08-15T23:02:37.5648450Z               Size: 0 MB (26491 B)
2026-08-15T23:02:37.5648790Z               Time: 609 ms
2026-08-15T23:02:37.5649152Z               (Entry restored: exact match found)
2026-08-15T23:02:37.5649544Z     Saved     Key : 
2026-08-15T23:02:37.5649818Z               Size: 
2026-08-15T23:02:37.5650444Z               Time: 
2026-08-15T23:02:37.5650800Z               (Entry not saved: cache is read-only)
2026-08-15T23:02:37.5651190Z ---
2026-08-15T23:02:37.5651560Z Entry: wrapper\dists\gradle-9.4.1-bin\arn2x92ynaizyzdaamcbpbhtj
2026-08-15T23:02:37.5652191Z     Requested Key : gradle-wrapper-zips-v2-9db0835d029c62b1a3d29bf9e5532cf5
2026-08-15T23:02:37.5652635Z     Restored  Key : gradle-wrapper-zips-v2-9db0835d029c62b1a3d29bf9e5532cf5
2026-08-15T23:02:37.5653153Z               Size: 131 MB (137095041 B)
2026-08-15T23:02:37.5653381Z               Time: 3903 ms
2026-08-15T23:02:37.5653617Z               (Entry restored: exact match found)
2026-08-15T23:02:37.5653870Z     Saved     Key : 
2026-08-15T23:02:37.5654048Z               Size: 
2026-08-15T23:02:37.5654215Z               Time: 
2026-08-15T23:02:37.5654415Z               (Entry not saved: cache is read-only)
2026-08-15T23:02:37.5654642Z ---
2026-08-15T23:02:37.5654808Z Entry: dependencies
2026-08-15T23:02:37.5655101Z     Requested Key : gradle-dependencies-v2-779fb2e3e370d7bd63af1de1f466a0f1
2026-08-15T23:02:37.5655500Z     Restored  Key : gradle-dependencies-v2-779fb2e3e370d7bd63af1de1f466a0f1
2026-08-15T23:02:37.5655803Z               Size: 421 MB (441774729 B)
2026-08-15T23:02:37.5656021Z               Time: 6239 ms
2026-08-15T23:02:37.5656246Z               (Entry restored: exact match found)
2026-08-15T23:02:37.5656476Z     Saved     Key : 
2026-08-15T23:02:37.5656654Z               Size: 
2026-08-15T23:02:37.5656831Z               Time: 
2026-08-15T23:02:37.5657028Z               (Entry not saved: cache is read-only)
2026-08-15T23:02:37.5657256Z ---
2026-08-15T23:02:37.5657425Z Entry: instrumented-jars
2026-08-15T23:02:37.5657745Z     Requested Key : gradle-instrumented-jars-v2-daa0d421a72ed08fb55ec9059104e303
2026-08-15T23:02:37.5658182Z     Restored  Key : gradle-instrumented-jars-v2-daa0d421a72ed08fb55ec9059104e303
2026-08-15T23:02:37.5658509Z               Size: 0 MB (149241 B)
2026-08-15T23:02:37.5658730Z               Time: 544 ms
2026-08-15T23:02:37.5658944Z               (Entry restored: exact match found)
2026-08-15T23:02:37.5659172Z     Saved     Key : 
2026-08-15T23:02:37.5659346Z               Size: 
2026-08-15T23:02:37.5659518Z               Time: 
2026-08-15T23:02:37.5659706Z               (Entry not saved: cache is read-only)
2026-08-15T23:02:37.5659931Z ---
2026-08-15T23:02:37.5660088Z Entry: build-cache
2026-08-15T23:02:37.5660925Z     Requested Key : gradle-build-cache-v2-2e83b74aa3df19cd322c60e24b4e2409
2026-08-15T23:02:37.5661338Z     Restored  Key : gradle-build-cache-v2-2e83b74aa3df19cd322c60e24b4e2409
2026-08-15T23:02:37.5661644Z               Size: 2 MB (1869848 B)
2026-08-15T23:02:37.5661868Z               Time: 1011 ms
2026-08-15T23:02:37.5662083Z               (Entry restored: exact match found)
2026-08-15T23:02:37.5662322Z     Saved     Key : 
2026-08-15T23:02:37.5662504Z               Size: 
2026-08-15T23:02:37.5662682Z               Time: 
2026-08-15T23:02:37.5662877Z               (Entry not saved: cache is read-only)
2026-08-15T23:02:37.5663105Z ---
2026-08-15T23:02:37.5663266Z Entry: groovy-dsl
2026-08-15T23:02:37.5663540Z     Requested Key : gradle-groovy-dsl-v2-437faa181b2dc2b3927efe77648cfd79
2026-08-15T23:02:37.5663922Z     Restored  Key : gradle-groovy-dsl-v2-437faa181b2dc2b3927efe77648cfd79
2026-08-15T23:02:37.5664219Z               Size: 0 MB (228714 B)
2026-08-15T23:02:37.5664451Z               Time: 1223 ms
2026-08-15T23:02:37.5664671Z               (Entry restored: exact match found)
2026-08-15T23:02:37.5664911Z     Saved     Key : 
2026-08-15T23:02:37.5665096Z               Size: 
2026-08-15T23:02:37.5665286Z               Time: 
2026-08-15T23:02:37.5665581Z               (Entry not saved: cache is read-only)
2026-08-15T23:02:37.5665967Z ---
2026-08-15T23:02:37.5684482Z Entry: transforms
2026-08-15T23:02:37.5684976Z     Requested Key : gradle-transforms-v2-af0191dc0d0373634d8ba42794141fa0
2026-08-15T23:02:37.5685648Z     Restored  Key : gradle-transforms-v2-af0191dc0d0373634d8ba42794141fa0
2026-08-15T23:02:37.5686166Z               Size: 28 MB (29882255 B)
2026-08-15T23:02:37.5686535Z               Time: 3018 ms
2026-08-15T23:02:37.5686902Z               (Entry restored: exact match found)
2026-08-15T23:02:37.5687306Z     Saved     Key : 
2026-08-15T23:02:37.5687593Z               Size: 
2026-08-15T23:02:37.5687879Z               Time: 
2026-08-15T23:02:37.5688423Z               (Entry not saved: cache is read-only)
2026-08-15T23:02:37.5688800Z </pre>
2026-08-15T23:02:37.5689050Z </details>
2026-08-15T23:02:37.5689208Z 
2026-08-15T23:02:37.5689567Z ##[endgroup]
2026-08-15T23:02:37.5689859Z Completed post-action step
2026-08-15T23:02:37.6562162Z Post job cleanup.
2026-08-15T23:02:37.8072088Z Post job cleanup.
2026-08-15T23:02:37.9596661Z [command]"C:\Program Files\Git\bin\git.exe" version
2026-08-15T23:02:37.9815760Z git version 2.55.0.windows.3
2026-08-15T23:02:37.9865922Z Temporarily overriding HOME='D:\a\_temp\bd0e0edd-10bf-4a1a-9465-402115aaefda' before making global git config changes
2026-08-15T23:02:37.9866901Z Adding repository directory to the temporary git global config as a safe directory
2026-08-15T23:02:37.9874345Z [command]"C:\Program Files\Git\bin\git.exe" config --global --add safe.directory D:\a\spotless\spotless
2026-08-15T23:02:38.0103791Z Removing SSH command configuration
2026-08-15T23:02:38.0112427Z [command]"C:\Program Files\Git\bin\git.exe" config --local --name-only --get-regexp core\.sshCommand
2026-08-15T23:02:38.0345456Z [command]"C:\Program Files\Git\bin\git.exe" submodule foreach --recursive "sh -c \"git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :\""
2026-08-15T23:02:38.4596534Z Removing HTTP extra header
2026-08-15T23:02:38.4605126Z [command]"C:\Program Files\Git\bin\git.exe" config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-08-15T23:02:38.4851986Z [command]"C:\Program Files\Git\bin\git.exe" submodule foreach --recursive "sh -c \"git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :\""
2026-08-15T23:02:38.9189651Z Removing includeIf entries pointing to credentials config files
2026-08-15T23:02:38.9200015Z [command]"C:\Program Files\Git\bin\git.exe" config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-08-15T23:02:38.9404909Z includeif.gitdir:D:/a/spotless/spotless/.git.path
2026-08-15T23:02:38.9405493Z includeif.gitdir:D:/a/spotless/spotless/.git/worktrees/*.path
2026-08-15T23:02:38.9405979Z includeif.gitdir:/github/workspace/.git.path
2026-08-15T23:02:38.9406482Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-08-15T23:02:38.9437470Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all includeif.gitdir:D:/a/spotless/spotless/.git.path
2026-08-15T23:02:38.9637087Z D:\a\_temp\git-credentials-ad9fc381-7f32-4172-aba1-01ca341c423e.config
2026-08-15T23:02:38.9670160Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset includeif.gitdir:D:/a/spotless/spotless/.git.path D:\a\_temp\git-credentials-ad9fc381-7f32-4172-aba1-01ca341c423e.config
2026-08-15T23:02:38.9899719Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all includeif.gitdir:D:/a/spotless/spotless/.git/worktrees/*.path
2026-08-15T23:02:39.0097332Z D:\a\_temp\git-credentials-ad9fc381-7f32-4172-aba1-01ca341c423e.config
2026-08-15T23:02:39.0129629Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset includeif.gitdir:D:/a/spotless/spotless/.git/worktrees/*.path D:\a\_temp\git-credentials-ad9fc381-7f32-4172-aba1-01ca341c423e.config
2026-08-15T23:02:39.0434501Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-08-15T23:02:39.0676565Z /github/runner_temp/git-credentials-ad9fc381-7f32-4172-aba1-01ca341c423e.config
2026-08-15T23:02:39.0708129Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset includeif.gitdir:/github/workspace/.git.path /github/runner_temp/git-credentials-ad9fc381-7f32-4172-aba1-01ca341c423e.config
2026-08-15T23:02:39.0952275Z [command]"C:\Program Files\Git\bin\git.exe" config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-08-15T23:02:39.1155266Z /github/runner_temp/git-credentials-ad9fc381-7f32-4172-aba1-01ca341c423e.config
2026-08-15T23:02:39.1186847Z [command]"C:\Program Files\Git\bin\git.exe" config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path /github/runner_temp/git-credentials-ad9fc381-7f32-4172-aba1-01ca341c423e.config
2026-08-15T23:02:39.1428773Z [command]"C:\Program Files\Git\bin\git.exe" submodule foreach --recursive "git config --local --show-origin --name-only --get-regexp remote.origin.url"
2026-08-15T23:02:39.5369207Z Removing credentials config 'D:\a\_temp\git-credentials-ad9fc381-7f32-4172-aba1-01ca341c423e.config'
2026-08-15T23:02:39.5538516Z Cleaning up orphan processes
2026-08-15T23:02:39.5735999Z Terminate orphan process: pid (7140) (java)
2026-08-15T23:02:39.6070717Z Terminate orphan process: pid (968) (java)
2026-08-15T23:02:39.6140048Z Terminate orphan process: pid (1904) (conhost)
2026-08-15T23:02:39.6650020Z Terminate orphan process: pid (7656) (java)
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 23. `farama-foundation__highwayenv__082832194425.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/farama-foundation__highwayenv__082832194425.txt` (authoritative; read this, not the excerpt)
- **Repository**: `farama-foundation/highwayenv`
- **Content hash (sha256, first 16)**: `2b70a6572e313d07`
- **Body size**: 117,323 bytes, 1,197 lines
- **Excerpt**: final 120 of 1,197 lines, content-blind

```text
2026-06-22T22:11:27.1552756Z shell: /usr/bin/bash -e {0}
2026-06-22T22:11:27.1553012Z env:
2026-06-22T22:11:27.1553283Z   pythonLocation: /opt/hostedtoolcache/Python/3.11.15/x64
2026-06-22T22:11:27.1553701Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib/pkgconfig
2026-06-22T22:11:27.1554122Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-06-22T22:11:27.1554487Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-06-22T22:11:27.1554846Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-06-22T22:11:27.1555211Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib
2026-06-22T22:11:27.1555523Z ##[endgroup]
2026-06-22T22:11:30.7309138Z ============================= test session starts ==============================
2026-06-22T22:11:30.7310384Z platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
2026-06-22T22:11:30.7310830Z rootdir: /home/runner/work/HighwayEnv/HighwayEnv
2026-06-22T22:11:30.7311189Z configfile: pyproject.toml
2026-06-22T22:11:30.7311463Z plugins: cov-7.1.0
2026-06-22T22:11:30.7311700Z collected 110 items
2026-06-22T22:11:30.7311843Z 
2026-06-22T22:11:36.0165612Z tests/envs/test_actions.py ...                                           [  2%]
2026-06-22T22:11:37.8117239Z tests/envs/test_env_preprocessors.py .                                   [  3%]
2026-06-22T22:12:21.0760013Z tests/envs/test_gym.py ........ss....................................... [ 48%]
2026-06-22T22:12:23.1308882Z ........                                                                 [ 55%]
2026-06-22T22:12:36.7345633Z tests/envs/test_multiprocessing.py ............                          [ 66%]
2026-06-22T22:12:36.7786479Z tests/envs/test_observations.py .                                        [ 67%]
2026-06-22T22:12:43.2474201Z tests/envs/test_time.py .                                                [ 68%]
2026-06-22T22:12:43.4671705Z tests/graphics/test_render.py ....                                       [ 71%]
2026-06-22T22:12:43.4900768Z tests/road/test_neighbour_vehicles.py ...............                    [ 85%]
2026-06-22T22:12:43.5466393Z tests/road/test_road.py ...                                              [ 88%]
2026-06-22T22:12:43.5487141Z tests/test_utils.py .                                                    [ 89%]
2026-06-22T22:12:43.6045177Z tests/vehicle/test_behavior.py ..                                        [ 90%]
2026-06-22T22:12:43.6155552Z tests/vehicle/test_control.py ...                                        [ 93%]
2026-06-22T22:12:43.6247444Z tests/vehicle/test_dynamics.py .....                                     [ 98%]
2026-06-22T22:12:44.9147770Z tests/vehicle/test_uncertainty.py ..                                     [100%]
2026-06-22T22:12:44.9148484Z 
2026-06-22T22:12:44.9148786Z =============================== warnings summary ===============================
2026-06-22T22:12:44.9149635Z tests/envs/test_gym.py::test_env_step[merge-v0]
2026-06-22T22:12:44.9150694Z tests/envs/test_gym.py::test_connected_lane_neighbour_versions[merge-v0-merge-v1]
2026-06-22T22:12:44.9151790Z tests/envs/test_gym.py::test_env_vectorization__info_dtype_is_float[merge-v0]
2026-06-22T22:12:44.9152828Z tests/envs/test_gym.py::test_env_vectorization__info_dtype_is_float[merge-v0]
2026-06-22T22:12:44.9153723Z tests/graphics/test_render.py::test_render[merge-v0]
2026-06-22T22:12:44.9154170Z tests/graphics/test_render.py::test_obs_grayscale[merge-v0]
2026-06-22T22:12:44.9155673Z   /opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/gymnasium/envs/registration.py:513: DeprecationWarning: [33mWARN: The environment merge-v0 is out of date. You should consider upgrading to version `v1`.[0m
2026-06-22T22:12:44.9156712Z     logger.deprecation(
2026-06-22T22:12:44.9156886Z 
2026-06-22T22:12:44.9157049Z tests/envs/test_gym.py::test_env_step[roundabout-v0]
2026-06-22T22:12:44.9157756Z tests/envs/test_gym.py::test_connected_lane_neighbour_versions[roundabout-v0-roundabout-v1]
2026-06-22T22:12:44.9158417Z tests/envs/test_gym.py::test_env_vectorization__info_dtype_is_float[roundabout-v0]
2026-06-22T22:12:44.9159017Z tests/envs/test_gym.py::test_env_vectorization__info_dtype_is_float[roundabout-v0]
2026-06-22T22:12:44.9160599Z   /opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/gymnasium/envs/registration.py:513: DeprecationWarning: [33mWARN: The environment roundabout-v0 is out of date. You should consider upgrading to version `v1`.[0m
2026-06-22T22:12:44.9161640Z     logger.deprecation(
2026-06-22T22:12:44.9161803Z 
2026-06-22T22:12:44.9161976Z tests/envs/test_gym.py::test_env_step[intersection-v0]
2026-06-22T22:12:44.9162550Z tests/envs/test_gym.py::test_connected_lane_neighbour_versions[intersection-v0-intersection-v2]
2026-06-22T22:12:44.9163216Z tests/envs/test_gym.py::test_env_vectorization__info_dtype_is_float[intersection-v0]
2026-06-22T22:12:44.9163832Z tests/envs/test_gym.py::test_env_vectorization__info_dtype_is_float[intersection-v0]
2026-06-22T22:12:44.9165181Z   /opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/gymnasium/envs/registration.py:513: DeprecationWarning: [33mWARN: The environment intersection-v0 is out of date. You should consider upgrading to version `v2`.[0m
2026-06-22T22:12:44.9166206Z     logger.deprecation(
2026-06-22T22:12:44.9166372Z 
2026-06-22T22:12:44.9166540Z tests/envs/test_gym.py::test_env_step[intersection-v1]
2026-06-22T22:12:44.9167045Z tests/envs/test_gym.py::test_env_vectorization__info_dtype_is_float[intersection-v1]
2026-06-22T22:12:44.9167653Z tests/envs/test_gym.py::test_env_vectorization__info_dtype_is_float[intersection-v1]
2026-06-22T22:12:44.9168985Z   /opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/gymnasium/envs/registration.py:513: DeprecationWarning: [33mWARN: The environment intersection-v1 is out of date. You should consider upgrading to version `v2`.[0m
2026-06-22T22:12:44.9170041Z     logger.deprecation(
2026-06-22T22:12:44.9170219Z 
2026-06-22T22:12:44.9170371Z tests/envs/test_gym.py::test_env_step[racetrack-v0]
2026-06-22T22:12:44.9170820Z tests/envs/test_gym.py::test_connected_lane_neighbour_versions[racetrack-v0-racetrack-v1]
2026-06-22T22:12:44.9171367Z tests/envs/test_gym.py::test_env_vectorization__info_dtype_is_float[racetrack-v0]
2026-06-22T22:12:44.9171867Z tests/envs/test_gym.py::test_env_vectorization__info_dtype_is_float[racetrack-v0]
2026-06-22T22:12:44.9172962Z   /opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/gymnasium/envs/registration.py:513: DeprecationWarning: [33mWARN: The environment racetrack-v0 is out of date. You should consider upgrading to version `v1`.[0m
2026-06-22T22:12:44.9173821Z     logger.deprecation(
2026-06-22T22:12:44.9173966Z 
2026-06-22T22:12:44.9174278Z tests/envs/test_gym.py::test_connected_lane_neighbour_versions[exit-v0-exit-v1]
2026-06-22T22:12:44.9175397Z   /opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/gymnasium/envs/registration.py:513: DeprecationWarning: [33mWARN: The environment exit-v0 is out of date. You should consider upgrading to version `v1`.[0m
2026-06-22T22:12:44.9176257Z     logger.deprecation(
2026-06-22T22:12:44.9176385Z 
2026-06-22T22:12:44.9176699Z tests/envs/test_gym.py::test_connected_lane_neighbour_versions[roundabout-generic-v0-roundabout-generic-v1]
2026-06-22T22:12:44.9178046Z   /opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/gymnasium/envs/registration.py:513: DeprecationWarning: [33mWARN: The environment roundabout-generic-v0 is out of date. You should consider upgrading to version `v1`.[0m
2026-06-22T22:12:44.9178905Z     logger.deprecation(
2026-06-22T22:12:44.9179042Z 
2026-06-22T22:12:44.9179329Z tests/envs/test_gym.py::test_connected_lane_neighbour_versions[racetrack-large-v0-racetrack-large-v1]
2026-06-22T22:12:44.9180689Z   /opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/gymnasium/envs/registration.py:513: DeprecationWarning: [33mWARN: The environment racetrack-large-v0 is out of date. You should consider upgrading to version `v1`.[0m
2026-06-22T22:12:44.9181537Z     logger.deprecation(
2026-06-22T22:12:44.9181667Z 
2026-06-22T22:12:44.9181947Z tests/envs/test_gym.py::test_connected_lane_neighbour_versions[racetrack-oval-v0-racetrack-oval-v1]
2026-06-22T22:12:44.9183123Z   /opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/gymnasium/envs/registration.py:513: DeprecationWarning: [33mWARN: The environment racetrack-oval-v0 is out of date. You should consider upgrading to version `v1`.[0m
2026-06-22T22:12:44.9183967Z     logger.deprecation(
2026-06-22T22:12:44.9184102Z 
2026-06-22T22:12:44.9184320Z tests/envs/test_gym.py::test_connected_lane_neighbour_versions[u-turn-v0-u-turn-v1]
2026-06-22T22:12:44.9185405Z   /opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/gymnasium/envs/registration.py:513: DeprecationWarning: [33mWARN: The environment u-turn-v0 is out of date. You should consider upgrading to version `v1`.[0m
2026-06-22T22:12:44.9186225Z     logger.deprecation(
2026-06-22T22:12:44.9186353Z 
2026-06-22T22:12:44.9186717Z tests/envs/test_gym.py::test_connected_lane_neighbour_versions[intersection-multi-agent-v0-intersection-multi-agent-v2]
2026-06-22T22:12:44.9188014Z   /opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/gymnasium/envs/registration.py:513: DeprecationWarning: [33mWARN: The environment intersection-multi-agent-v0 is out of date. You should consider upgrading to version `v2`.[0m
2026-06-22T22:12:44.9188900Z     logger.deprecation(
2026-06-22T22:12:44.9189037Z 
2026-06-22T22:12:44.9189242Z -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2026-06-22T22:12:44.9189815Z ================================ tests coverage ================================
2026-06-22T22:12:44.9190342Z _______________ coverage: platform linux, python 3.11.15-final-0 _______________
2026-06-22T22:12:44.9190618Z 
2026-06-22T22:12:44.9190730Z Coverage XML written to file coverage.xml
2026-06-22T22:12:44.9191080Z ============ 108 passed, 2 skipped, 27 warnings in 77.07s (0:01:17) ============
2026-06-22T22:12:45.1215826Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-22T22:12:45.1216996Z Post job cleanup.
2026-06-22T22:12:45.2377255Z (node:4278) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-06-22T22:12:45.2378393Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-06-22T22:12:45.2519237Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-22T22:12:45.2520505Z Post job cleanup.
2026-06-22T22:12:45.3317246Z [command]/usr/bin/git version
2026-06-22T22:12:45.3351256Z git version 2.54.0
2026-06-22T22:12:45.3384227Z Temporarily overriding HOME='/home/runner/work/_temp/585d7c5a-b0eb-40e0-912b-bce133bf86ef' before making global git config changes
2026-06-22T22:12:45.3385688Z Adding repository directory to the temporary git global config as a safe directory
2026-06-22T22:12:45.3389598Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/HighwayEnv/HighwayEnv
2026-06-22T22:12:45.3425334Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-06-22T22:12:45.3455636Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-06-22T22:12:45.3634183Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-06-22T22:12:45.3657386Z http.https://github.com/.extraheader
2026-06-22T22:12:45.3666541Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-06-22T22:12:45.3692451Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-06-22T22:12:45.3862904Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-06-22T22:12:45.3889279Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-06-22T22:12:45.4195746Z Cleaning up orphan processes
2026-06-22T22:12:45.4472370Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/checkout@v4, actions/setup-python@v5. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 24. `fla-org__flash-linear-attention__082350718781.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/fla-org__flash-linear-attention__082350718781.txt` (authoritative; read this, not the excerpt)
- **Repository**: `fla-org/flash-linear-attention`
- **Content hash (sha256, first 16)**: `20031117edd68219`
- **Body size**: 79,260 bytes, 795 lines
- **Excerpt**: final 120 of 795 lines, content-blind

```text
2026-06-19T12:37:27.8829836Z ##[endgroup]
2026-06-19T12:37:45.1968517Z ============================= test session starts ==============================
2026-06-19T12:37:45.1969329Z platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /home/ubuntu/miniconda3/envs/pytorch_2_12/bin/python3.12
2026-06-19T12:37:45.1969816Z cachedir: .pytest_cache
2026-06-19T12:37:45.1970373Z rootdir: /home/ubuntu/actions-runner/_work/flash-linear-attention/flash-linear-attention
2026-06-19T12:37:45.1970858Z configfile: pyproject.toml
2026-06-19T12:37:45.1971102Z plugins: anyio-4.13.0
2026-06-19T12:37:45.2470104Z collecting ... collected 85 items
2026-06-19T12:37:45.2470311Z 
2026-06-19T12:37:45.2492240Z tests/layers/test_attn_varlen_pack_layout.py::test_attention_varlen_accepts_batched_layout_with_cu_seqlens[2-8-2-64] SKIPPED
2026-06-19T12:37:45.2498929Z tests/layers/test_attn_varlen_pack_layout.py::test_attention_varlen_accepts_batched_layout_with_cu_seqlens[3-7-4-32] SKIPPED
2026-06-19T12:37:45.6574959Z tests/layers/test_layer_cache_layer_idx.py::test_cache_requires_layer_idx[linear_attn] FAILED
2026-06-19T12:37:45.6575377Z 
2026-06-19T12:37:45.6575526Z =================================== FAILURES ===================================
2026-06-19T12:37:45.6575932Z __________________ test_cache_requires_layer_idx[linear_attn] __________________
2026-06-19T12:37:45.6576204Z 
2026-06-19T12:37:45.6576448Z builder = <function <lambda> at 0x7f84cd62e340>
2026-06-19T12:37:45.6576967Z hidden_states = tensor([[[-0.6171,  0.1915, -1.2230, -0.3240, -1.5177, -0.5093,  0.4517,
2026-06-19T12:37:45.6577381Z            0.0712, -0.2195, -1.3599,  0.8797,....1647,  1.3721,
2026-06-19T12:37:45.6577813Z            0.4305, -1.4890,  1.3532, -1.4380,  0.7022,  0.3029, -2.0586,
2026-06-19T12:37:45.6578129Z           -0.4891,  0.0490]]])
2026-06-19T12:37:45.6578276Z 
2026-06-19T12:37:45.6578389Z     @pytest.mark.parametrize(
2026-06-19T12:37:45.6578641Z         ("builder", "hidden_states"),
2026-06-19T12:37:45.6579400Z         CACHE_REQUIRES_LAYER_IDX_CASES,
2026-06-19T12:37:45.6579653Z     )
2026-06-19T12:37:45.6579901Z     def test_cache_requires_layer_idx(builder, hidden_states):
2026-06-19T12:37:45.6580317Z >       layer, hidden_states = prepare_layer_and_inputs(builder, hidden_states)
2026-06-19T12:37:45.6580696Z                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-06-19T12:37:45.6580906Z 
2026-06-19T12:37:45.6581039Z tests/layers/test_layer_cache_layer_idx.py:183: 
2026-06-19T12:37:45.6581569Z _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
2026-06-19T12:37:45.6581985Z tests/layers/test_layer_cache_layer_idx.py:54: in prepare_layer_and_inputs
2026-06-19T12:37:45.6582353Z     layer = maybe_build(builder).to(device)
2026-06-19T12:37:45.6582633Z             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-06-19T12:37:45.6583105Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/nn/modules/module.py:1383: in to
2026-06-19T12:37:45.6583585Z     return self._apply(convert)
2026-06-19T12:37:45.6583823Z            ^^^^^^^^^^^^^^^^^^^^
2026-06-19T12:37:45.6584238Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/nn/modules/module.py:933: in _apply
2026-06-19T12:37:45.6584674Z     module._apply(fn)
2026-06-19T12:37:45.6585070Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/nn/modules/module.py:933: in _apply
2026-06-19T12:37:45.6585507Z     module._apply(fn)
2026-06-19T12:37:45.6585959Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/nn/modules/module.py:964: in _apply
2026-06-19T12:37:45.6586409Z     param_applied = fn(param)
2026-06-19T12:37:45.6586701Z                     ^^^^^^^^^
2026-06-19T12:37:45.6587116Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/nn/modules/module.py:1369: in convert
2026-06-19T12:37:45.6587551Z     return t.to(
2026-06-19T12:37:45.6587806Z _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
2026-06-19T12:37:45.6588031Z 
2026-06-19T12:37:45.6588113Z     def _lazy_init():
2026-06-19T12:37:45.6588373Z         global _initialized, _queued_calls
2026-06-19T12:37:45.6588700Z         if is_initialized() or hasattr(_tls, "is_initializing"):
2026-06-19T12:37:45.6589001Z             return
2026-06-19T12:37:45.6589235Z         with _initialization_lock:
2026-06-19T12:37:45.6589540Z             # We be double-checked locking, boys!  This is OK because
2026-06-19T12:37:45.6589918Z             # the above test was GIL protected anyway.  The inner test
2026-06-19T12:37:45.6590295Z             # is for when a thread blocked on some other thread which was
2026-06-19T12:37:45.6590685Z             # doing the initialization; when they get the lock, they will
2026-06-19T12:37:45.6591025Z             # find there is nothing left to do.
2026-06-19T12:37:45.6591299Z             if is_initialized():
2026-06-19T12:37:45.6591529Z                 return
2026-06-19T12:37:45.6591820Z             # It is important to prevent other threads from entering _lazy_init
2026-06-19T12:37:45.6592261Z             # immediately, while we are still guaranteed to have the GIL, because some
2026-06-19T12:37:45.6592669Z             # of the C calls we make below will release the GIL
2026-06-19T12:37:45.6592966Z             if _is_in_bad_fork():
2026-06-19T12:37:45.6593210Z                 raise RuntimeError(
2026-06-19T12:37:45.6593556Z                     "Cannot re-initialize CUDA in forked subprocess. To use CUDA with "
2026-06-19T12:37:45.6593981Z                     "multiprocessing, you must use the 'spawn' start method"
2026-06-19T12:37:45.6594291Z                 )
2026-06-19T12:37:45.6594544Z             if not hasattr(torch._C, "_cuda_getDeviceCount"):
2026-06-19T12:37:45.6594913Z                 raise AssertionError("Torch not compiled with CUDA enabled")
2026-06-19T12:37:45.6595237Z             if _cudart is None:
2026-06-19T12:37:45.6595479Z                 raise AssertionError(
2026-06-19T12:37:45.6595851Z                     "libcudart functions unavailable. It looks like you have a broken build?"
2026-06-19T12:37:45.6596315Z                 )
2026-06-19T12:37:45.6596619Z             # This function throws if there's a driver initialization error, no GPUs
2026-06-19T12:37:45.6596992Z             # are found or any other error occurs
2026-06-19T12:37:45.6597263Z >           torch._C._cuda_init()
2026-06-19T12:37:45.6597540Z E           RuntimeError: No CUDA GPUs are available
2026-06-19T12:37:45.6597743Z 
2026-06-19T12:37:45.6598108Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/cuda/__init__.py:491: RuntimeError
2026-06-19T12:37:45.6598599Z =============================== warnings summary ===============================
2026-06-19T12:37:45.6598917Z fla/utils/_device.py:100
2026-06-19T12:37:45.6599576Z   /home/ubuntu/actions-runner/_work/flash-linear-attention/flash-linear-attention/fla/utils/_device.py:100: UserWarning: Triton is not supported on current platform, roll back to CPU.
2026-06-19T12:37:45.6600247Z     _cpu_device_warning()
2026-06-19T12:37:45.6600383Z 
2026-06-19T12:37:45.6600623Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/cuda/__init__.py:1074
2026-06-19T12:37:45.6601160Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/cuda/__init__.py:1074
2026-06-19T12:37:45.6601689Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/cuda/__init__.py:1074
2026-06-19T12:37:45.6602347Z   /home/ubuntu/miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/cuda/__init__.py:1074: UserWarning: Can't initialize NVML
2026-06-19T12:37:45.6602885Z     raw_cnt = _raw_device_count_nvml()
2026-06-19T12:37:45.6603058Z 
2026-06-19T12:37:45.6603319Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/jit/_script.py:365: 14 warnings
2026-06-19T12:37:45.6604257Z   /home/ubuntu/miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/jit/_script.py:365: DeprecationWarning: `torch.jit.script_method` is deprecated. Please switch to `torch.compile` or `torch.export`.
2026-06-19T12:37:45.6604993Z     warnings.warn(
2026-06-19T12:37:45.6605115Z 
2026-06-19T12:37:45.6605321Z -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2026-06-19T12:37:45.6605726Z =========================== short test summary info ============================
2026-06-19T12:37:45.6606319Z FAILED tests/layers/test_layer_cache_layer_idx.py::test_cache_requires_layer_idx[linear_attn] - RuntimeError: No CUDA GPUs are available
2026-06-19T12:37:45.6606891Z !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
2026-06-19T12:37:45.6607261Z ================== 1 failed, 2 skipped, 18 warnings in 0.13s ===================
2026-06-19T12:37:46.6018663Z ##[error]Process completed with exit code 1.
2026-06-19T12:37:46.6128132Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-19T12:37:46.6129368Z Post job cleanup.
2026-06-19T12:37:46.6926100Z [command]/usr/bin/git version
2026-06-19T12:37:46.6955976Z git version 2.34.1
2026-06-19T12:37:46.6981466Z Copying '/home/ubuntu/.gitconfig' to '/home/ubuntu/actions-runner/_work/_temp/6e2783ac-1b77-4f29-bb5a-533cd9e8abcc/.gitconfig'
2026-06-19T12:37:46.6989904Z Temporarily overriding HOME='/home/ubuntu/actions-runner/_work/_temp/6e2783ac-1b77-4f29-bb5a-533cd9e8abcc' before making global git config changes
2026-06-19T12:37:46.6991003Z Adding repository directory to the temporary git global config as a safe directory
2026-06-19T12:37:46.6993519Z [command]/usr/bin/git config --global --add safe.directory /home/ubuntu/actions-runner/_work/flash-linear-attention/flash-linear-attention
2026-06-19T12:37:46.7020529Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-06-19T12:37:46.7045492Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-06-19T12:37:46.7225089Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-06-19T12:37:46.7241683Z http.https://github.com/.extraheader
2026-06-19T12:37:46.7248561Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-06-19T12:37:46.7271643Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-06-19T12:37:46.7475955Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-06-19T12:37:46.7498419Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-06-19T12:37:46.7803677Z Cleaning up orphan processes
2026-06-19T12:37:46.8020686Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/checkout@v4. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 25. `fla-org__flash-linear-attention__082477100071.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/fla-org__flash-linear-attention__082477100071.txt` (authoritative; read this, not the excerpt)
- **Repository**: `fla-org/flash-linear-attention`
- **Content hash (sha256, first 16)**: `d2fe7507ebde424d`
- **Body size**: 66,338 bytes, 729 lines
- **Excerpt**: final 120 of 729 lines, content-blind

```text
2026-06-20T10:45:37.0971186Z             ]
2026-06-20T10:45:37.0971374Z         ],
2026-06-20T10:45:37.0971563Z     )
2026-06-20T10:45:37.0971750Z     def test_modeling(
2026-06-20T10:45:37.0971962Z         L: int,
2026-06-20T10:45:37.0972153Z         B: int,
2026-06-20T10:45:37.0972340Z         T: int,
2026-06-20T10:45:37.0972519Z         H: int,
2026-06-20T10:45:37.0972699Z         D: int,
2026-06-20T10:45:37.0972896Z         use_l2warp: bool,
2026-06-20T10:45:37.0973133Z         attnres_block_size: int | None,
2026-06-20T10:45:37.0973394Z         dtype: torch.dtype,
2026-06-20T10:45:37.0973612Z     ):
2026-06-20T10:45:37.0973812Z >       run_test_model_forward_backward(
2026-06-20T10:45:37.0974058Z             L,
2026-06-20T10:45:37.0974251Z             B,
2026-06-20T10:45:37.0974433Z             T,
2026-06-20T10:45:37.0974614Z             H,
2026-06-20T10:45:37.0974795Z             D,
2026-06-20T10:45:37.0974983Z             NSAConfig,
2026-06-20T10:45:37.0975206Z             use_l2warp=use_l2warp,
2026-06-20T10:45:37.0975476Z             attnres_block_size=attnres_block_size,
2026-06-20T10:45:37.0976264Z             dtype=dtype,
2026-06-20T10:45:37.0976495Z         )
2026-06-20T10:45:37.0976656Z 
2026-06-20T10:45:37.0976778Z tests/models/test_modeling_nsa.py:42: 
2026-06-20T10:45:37.0977097Z _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
2026-06-20T10:45:37.0977500Z tests/models/test_modeling_base.py:53: in run_test_model_forward_backward
2026-06-20T10:45:37.0978047Z     model, config = create_model_and_config(config_class, L, H, D, use_l2warp=use_l2warp, dtype=dtype, **kwargs)
2026-06-20T10:45:37.0978555Z                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-06-20T10:45:37.0978968Z tests/models/test_modeling_utils.py:50: in create_model_and_config
2026-06-20T10:45:37.0979307Z     model.to(dtype).to(device)
2026-06-20T10:45:37.0979753Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/transformers/modeling_utils.py:3729: in to
2026-06-20T10:45:37.0980424Z     return super().to(*args, **kwargs)
2026-06-20T10:45:37.0980682Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-06-20T10:45:37.0981114Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/nn/modules/module.py:1383: in to
2026-06-20T10:45:37.0981564Z     return self._apply(convert)
2026-06-20T10:45:37.0981806Z            ^^^^^^^^^^^^^^^^^^^^
2026-06-20T10:45:37.0982222Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/nn/modules/module.py:933: in _apply
2026-06-20T10:45:37.0982669Z     module._apply(fn)
2026-06-20T10:45:37.0983072Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/nn/modules/module.py:933: in _apply
2026-06-20T10:45:37.0983515Z     module._apply(fn)
2026-06-20T10:45:37.0983908Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/nn/modules/module.py:964: in _apply
2026-06-20T10:45:37.0984360Z     param_applied = fn(param)
2026-06-20T10:45:37.0984599Z                     ^^^^^^^^^
2026-06-20T10:45:37.0985021Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/nn/modules/module.py:1369: in convert
2026-06-20T10:45:37.0985463Z     return t.to(
2026-06-20T10:45:37.0985719Z _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
2026-06-20T10:45:37.0985935Z 
2026-06-20T10:45:37.0986018Z     def _lazy_init():
2026-06-20T10:45:37.0986248Z         global _initialized, _queued_calls
2026-06-20T10:45:37.0986568Z         if is_initialized() or hasattr(_tls, "is_initializing"):
2026-06-20T10:45:37.0986868Z             return
2026-06-20T10:45:37.0987082Z         with _initialization_lock:
2026-06-20T10:45:37.0987396Z             # We be double-checked locking, boys!  This is OK because
2026-06-20T10:45:37.0987767Z             # the above test was GIL protected anyway.  The inner test
2026-06-20T10:45:37.0988143Z             # is for when a thread blocked on some other thread which was
2026-06-20T10:45:37.0988536Z             # doing the initialization; when they get the lock, they will
2026-06-20T10:45:37.0988884Z             # find there is nothing left to do.
2026-06-20T10:45:37.0989160Z             if is_initialized():
2026-06-20T10:45:37.0989390Z                 return
2026-06-20T10:45:37.0989688Z             # It is important to prevent other threads from entering _lazy_init
2026-06-20T10:45:37.0990133Z             # immediately, while we are still guaranteed to have the GIL, because some
2026-06-20T10:45:37.0990539Z             # of the C calls we make below will release the GIL
2026-06-20T10:45:37.0990839Z             if _is_in_bad_fork():
2026-06-20T10:45:37.0991087Z                 raise RuntimeError(
2026-06-20T10:45:37.0991441Z                     "Cannot re-initialize CUDA in forked subprocess. To use CUDA with "
2026-06-20T10:45:37.0991880Z                     "multiprocessing, you must use the 'spawn' start method"
2026-06-20T10:45:37.0992199Z                 )
2026-06-20T10:45:37.0992448Z             if not hasattr(torch._C, "_cuda_getDeviceCount"):
2026-06-20T10:45:37.0992913Z                 raise AssertionError("Torch not compiled with CUDA enabled")
2026-06-20T10:45:37.0993254Z             if _cudart is None:
2026-06-20T10:45:37.0993501Z                 raise AssertionError(
2026-06-20T10:45:37.0993892Z                     "libcudart functions unavailable. It looks like you have a broken build?"
2026-06-20T10:45:37.0994266Z                 )
2026-06-20T10:45:37.0994755Z             # This function throws if there's a driver initialization error, no GPUs
2026-06-20T10:45:37.0995168Z             # are found or any other error occurs
2026-06-20T10:45:37.0995448Z >           torch._C._cuda_init()
2026-06-20T10:45:37.0995726Z E           RuntimeError: No CUDA GPUs are available
2026-06-20T10:45:37.0995934Z 
2026-06-20T10:45:37.0996227Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/cuda/__init__.py:491: RuntimeError
2026-06-20T10:45:37.0996809Z =============================== warnings summary ===============================
2026-06-20T10:45:37.0997127Z fla/utils/_device.py:100
2026-06-20T10:45:37.0997797Z   /home/ubuntu/actions-runner/_work/flash-linear-attention/flash-linear-attention/fla/utils/_device.py:100: UserWarning: Triton is not supported on current platform, roll back to CPU.
2026-06-20T10:45:37.0998487Z     _cpu_device_warning()
2026-06-20T10:45:37.0998635Z 
2026-06-20T10:45:37.0998869Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/cuda/__init__.py:1074
2026-06-20T10:45:37.0999422Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/cuda/__init__.py:1074
2026-06-20T10:45:37.0999960Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/cuda/__init__.py:1074
2026-06-20T10:45:37.1000640Z   /home/ubuntu/miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/cuda/__init__.py:1074: UserWarning: Can't initialize NVML
2026-06-20T10:45:37.1001211Z     raw_cnt = _raw_device_count_nvml()
2026-06-20T10:45:37.1001374Z 
2026-06-20T10:45:37.1001644Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/jit/_script.py:365: 14 warnings
2026-06-20T10:45:37.1002574Z   /home/ubuntu/miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/jit/_script.py:365: DeprecationWarning: `torch.jit.script_method` is deprecated. Please switch to `torch.compile` or `torch.export`.
2026-06-20T10:45:37.1003318Z     warnings.warn(
2026-06-20T10:45:37.1003447Z 
2026-06-20T10:45:37.1003651Z -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2026-06-20T10:45:37.1004060Z =========================== short test summary info ============================
2026-06-20T10:45:37.1004751Z FAILED tests/models/test_modeling_nsa.py::test_modeling[L4-B4-T1024-H4-D64-l2True-bsNone-torch.bfloat16] - RuntimeError: No CUDA GPUs are available
2026-06-20T10:45:37.1005386Z !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
2026-06-20T10:45:37.1005751Z ======================== 1 failed, 18 warnings in 0.66s ========================
2026-06-20T10:45:38.2889958Z ##[error]Process completed with exit code 1.
2026-06-20T10:45:38.3006206Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-20T10:45:38.3007423Z Post job cleanup.
2026-06-20T10:45:38.3886478Z [command]/usr/bin/git version
2026-06-20T10:45:38.3922583Z git version 2.34.1
2026-06-20T10:45:38.3963382Z Copying '/home/ubuntu/.gitconfig' to '/home/ubuntu/actions-runner/_work/_temp/91696746-5d5c-4a23-a2f8-40034279c166/.gitconfig'
2026-06-20T10:45:38.3972280Z Temporarily overriding HOME='/home/ubuntu/actions-runner/_work/_temp/91696746-5d5c-4a23-a2f8-40034279c166' before making global git config changes
2026-06-20T10:45:38.3973238Z Adding repository directory to the temporary git global config as a safe directory
2026-06-20T10:45:38.3977606Z [command]/usr/bin/git config --global --add safe.directory /home/ubuntu/actions-runner/_work/flash-linear-attention/flash-linear-attention
2026-06-20T10:45:38.4009121Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-06-20T10:45:38.4037699Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-06-20T10:45:38.4238544Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-06-20T10:45:38.4258459Z http.https://github.com/.extraheader
2026-06-20T10:45:38.4267169Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-06-20T10:45:38.4294597Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-06-20T10:45:38.4483408Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-06-20T10:45:38.4508219Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-06-20T10:45:38.4823533Z Cleaning up orphan processes
2026-06-20T10:45:38.5086633Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/checkout@v4. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 26. `floci-io__floci__089834122110.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/floci-io__floci__089834122110.txt` (authoritative; read this, not the excerpt)
- **Repository**: `floci-io/floci`
- **Content hash (sha256, first 16)**: `3c332a181e22fc2b`
- **Body size**: 499,657 bytes, 3,760 lines
- **Excerpt**: final 120 of 3,760 lines, content-blind

```text
2026-07-26T19:48:12.1985832Z 2026-07-26 19:48:11,412 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-07-26T19:48:12.1986219Z 2026-07-26 19:48:11,412 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-7a5acc11 in region us-east-1 (version 1)
2026-07-26T19:48:12.1986562Z 2026-07-26 19:48:11,414 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: LabelParameterVersion
2026-07-26T19:48:12.1986967Z 2026-07-26 19:48:11,414 INFO  [io.git.hec.flo.ser.ssm.SsmService] Labeled parameter /pytest-sdk-test/pytest-7a5acc11 version 1 with labels [py-label]
2026-07-26T19:48:12.1987284Z 2026-07-26 19:48:11,416 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-07-26T19:48:12.1987577Z 2026-07-26 19:48:11,416 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-7a5acc11
2026-07-26T19:48:12.1987881Z 2026-07-26 19:48:11,422 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-07-26T19:48:12.1988269Z 2026-07-26 19:48:11,422 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-aea5b2c7 in region us-east-1 (version 1)
2026-07-26T19:48:12.1988607Z 2026-07-26 19:48:11,424 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: GetParameterHistory
2026-07-26T19:48:12.1989056Z 2026-07-26 19:48:11,426 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-07-26T19:48:12.1989385Z 2026-07-26 19:48:11,426 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-aea5b2c7
2026-07-26T19:48:12.1989693Z 2026-07-26 19:48:11,434 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-07-26T19:48:12.1990199Z 2026-07-26 19:48:11,434 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-9e0912c7 in region us-east-1 (version 1)
2026-07-26T19:48:12.1990529Z 2026-07-26 19:48:11,436 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: GetParameters
2026-07-26T19:48:12.1990853Z 2026-07-26 19:48:11,437 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-07-26T19:48:12.1991150Z 2026-07-26 19:48:11,438 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-9e0912c7
2026-07-26T19:48:12.1991458Z 2026-07-26 19:48:11,444 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-07-26T19:48:12.1991843Z 2026-07-26 19:48:11,444 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-a3ae8cfa in region us-east-1 (version 1)
2026-07-26T19:48:12.1992175Z 2026-07-26 19:48:11,446 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DescribeParameters
2026-07-26T19:48:12.1992494Z 2026-07-26 19:48:11,448 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-07-26T19:48:12.1992784Z 2026-07-26 19:48:11,448 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-a3ae8cfa
2026-07-26T19:48:12.1993268Z 2026-07-26 19:48:11,454 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-07-26T19:48:12.1993683Z 2026-07-26 19:48:11,454 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-2395e47d/param in region us-east-1 (version 1)
2026-07-26T19:48:12.1994016Z 2026-07-26 19:48:11,456 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: GetParametersByPath
2026-07-26T19:48:12.1994336Z 2026-07-26 19:48:11,458 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-07-26T19:48:12.1994645Z 2026-07-26 19:48:11,458 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-2395e47d/param
2026-07-26T19:48:12.1994953Z 2026-07-26 19:48:11,465 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-07-26T19:48:12.1995343Z 2026-07-26 19:48:11,465 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-bff25f73 in region us-east-1 (version 1)
2026-07-26T19:48:12.1995668Z 2026-07-26 19:48:11,467 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: AddTagsToResource
2026-07-26T19:48:12.1995990Z 2026-07-26 19:48:11,469 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-07-26T19:48:12.1996284Z 2026-07-26 19:48:11,469 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-bff25f73
2026-07-26T19:48:12.1996586Z 2026-07-26 19:48:11,477 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-07-26T19:48:12.1996973Z 2026-07-26 19:48:11,477 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-9ae39f87 in region us-east-1 (version 1)
2026-07-26T19:48:12.1997293Z 2026-07-26 19:48:11,479 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: AddTagsToResource
2026-07-26T19:48:12.1997628Z 2026-07-26 19:48:11,481 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: ListTagsForResource
2026-07-26T19:48:12.1998057Z 2026-07-26 19:48:11,483 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-07-26T19:48:12.1998405Z 2026-07-26 19:48:11,483 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-9ae39f87
2026-07-26T19:48:12.1998716Z 2026-07-26 19:48:11,489 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-07-26T19:48:12.1999108Z 2026-07-26 19:48:11,489 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-ceecb3ca in region us-east-1 (version 1)
2026-07-26T19:48:12.1999431Z 2026-07-26 19:48:11,491 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: AddTagsToResource
2026-07-26T19:48:12.1999778Z 2026-07-26 19:48:11,493 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: RemoveTagsFromResource
2026-07-26T19:48:12.2000283Z 2026-07-26 19:48:11,495 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: ListTagsForResource
2026-07-26T19:48:12.2000639Z 2026-07-26 19:48:11,497 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-07-26T19:48:12.2000936Z 2026-07-26 19:48:11,497 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-ceecb3ca
2026-07-26T19:48:12.2001238Z 2026-07-26 19:48:11,503 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-07-26T19:48:12.2001624Z 2026-07-26 19:48:11,503 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-fa0cd1ba in region us-east-1 (version 1)
2026-07-26T19:48:12.2001944Z 2026-07-26 19:48:11,505 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-07-26T19:48:12.2002425Z 2026-07-26 19:48:11,505 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-fa0cd1ba
2026-07-26T19:48:12.2002740Z 2026-07-26 19:48:11,507 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: GetParameter
2026-07-26T19:48:12.2003048Z 2026-07-26 19:48:11,518 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-07-26T19:48:12.2003453Z 2026-07-26 19:48:11,518 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-026c4b41/p1 in region us-east-1 (version 1)
2026-07-26T19:48:12.2003760Z 2026-07-26 19:48:11,520 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-07-26T19:48:12.2004155Z 2026-07-26 19:48:11,520 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-026c4b41/p2 in region us-east-1 (version 1)
2026-07-26T19:48:12.2004482Z 2026-07-26 19:48:11,522 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameters
2026-07-26T19:48:12.2099273Z Post job cleanup.
2026-07-26T19:48:12.4417332Z ##[group]Generating build summary
2026-07-26T19:48:12.4938010Z exporting build record to /home/runner/work/_temp/docker-actions-toolkit-S7GrjA/export
2026-07-26T19:48:12.5898720Z [command]/usr/bin/docker buildx history export --builder builder-a5679edf-87c5-4696-8467-f74d66759179 --output /home/runner/work/_temp/docker-actions-toolkit-S7GrjA/export/floci-io~floci~OY7PFW.dockerbuild oy7pfwwu1ckktz39r1lkl9hvg --finalize
2026-07-26T19:48:12.7324745Z Build record written to /home/runner/work/_temp/docker-actions-toolkit-S7GrjA/export/floci-io~floci~OY7PFW.dockerbuild (40.21 KB)
2026-07-26T19:48:12.7325928Z Uploading floci-io~floci~OY7PFW.dockerbuild as an artifact
2026-07-26T19:48:12.7329719Z Artifact name is valid!
2026-07-26T19:48:12.7332833Z Root directory input is valid!
2026-07-26T19:48:12.9463892Z Uploading artifact: floci-io~floci~OY7PFW.dockerbuild
2026-07-26T19:48:12.9498505Z Beginning upload of artifact content to blob storage
2026-07-26T19:48:13.1252888Z Uploaded bytes 41180
2026-07-26T19:48:13.1637444Z Finished uploading artifact content to blob storage!
2026-07-26T19:48:13.1638008Z SHA256 digest of uploaded artifact is 4a69a9bb98e48bf3cb6d1b0ff39be2deaea27fb52f61a06c3de8a1f3cc9693bc
2026-07-26T19:48:13.1638484Z Finalizing artifact upload
2026-07-26T19:48:13.4469045Z Artifact floci-io~floci~OY7PFW.dockerbuild successfully finalized. Artifact ID 8636257741
2026-07-26T19:48:13.4469716Z Artifact download URL: https://github.com/floci-io/floci/actions/runs/30196568684/artifacts/8636257741
2026-07-26T19:48:13.4490716Z Writing summary
2026-07-26T19:48:13.4502614Z ##[endgroup]
2026-07-26T19:48:13.4503086Z ##[group]Removing temp folder /home/runner/work/_temp/docker-actions-toolkit-iPUnPJ
2026-07-26T19:48:13.4506461Z ##[endgroup]
2026-07-26T19:48:13.4506796Z ##[group]Post cache
2026-07-26T19:48:13.4507187Z State not set
2026-07-26T19:48:13.4507635Z ##[endgroup]
2026-07-26T19:48:13.4659523Z Post job cleanup.
2026-07-26T19:48:13.6516840Z ##[group]Removing builder
2026-07-26T19:48:13.7342523Z [command]/usr/bin/docker buildx rm builder-a5679edf-87c5-4696-8467-f74d66759179
2026-07-26T19:48:13.9817787Z builder-a5679edf-87c5-4696-8467-f74d66759179 removed
2026-07-26T19:48:13.9843366Z ##[endgroup]
2026-07-26T19:48:13.9843729Z ##[group]Cleaning up certificates
2026-07-26T19:48:13.9846611Z ##[endgroup]
2026-07-26T19:48:13.9847369Z ##[group]Post cache
2026-07-26T19:48:13.9848531Z State not set
2026-07-26T19:48:13.9849648Z ##[endgroup]
2026-07-26T19:48:13.9991752Z Post job cleanup.
2026-07-26T19:48:14.0683538Z [command]/usr/bin/git version
2026-07-26T19:48:14.0721620Z git version 2.54.0
2026-07-26T19:48:14.0755558Z Temporarily overriding HOME='/home/runner/work/_temp/6d5caf47-2a02-486f-bb57-2126a28feca9' before making global git config changes
2026-07-26T19:48:14.0757682Z Adding repository directory to the temporary git global config as a safe directory
2026-07-26T19:48:14.0760583Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/floci/floci
2026-07-26T19:48:14.0791553Z Removing SSH command configuration
2026-07-26T19:48:14.0802267Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-07-26T19:48:14.0832576Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-07-26T19:48:14.1022062Z Removing HTTP extra header
2026-07-26T19:48:14.1026260Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-26T19:48:14.1056952Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-07-26T19:48:14.1245721Z Removing includeIf entries pointing to credentials config files
2026-07-26T19:48:14.1251519Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-26T19:48:14.1275753Z includeif.gitdir:/home/runner/work/floci/floci/.git.path
2026-07-26T19:48:14.1276196Z includeif.gitdir:/home/runner/work/floci/floci/.git/worktrees/*.path
2026-07-26T19:48:14.1276569Z includeif.gitdir:/github/workspace/.git.path
2026-07-26T19:48:14.1276897Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-26T19:48:14.1283126Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/floci/floci/.git.path
2026-07-26T19:48:14.1305274Z /home/runner/work/_temp/git-credentials-1dd8970b-bbee-479d-922b-ab310cd893b3.config
2026-07-26T19:48:14.1314667Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/floci/floci/.git.path /home/runner/work/_temp/git-credentials-1dd8970b-bbee-479d-922b-ab310cd893b3.config
2026-07-26T19:48:14.1347150Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/floci/floci/.git/worktrees/*.path
2026-07-26T19:48:14.1368915Z /home/runner/work/_temp/git-credentials-1dd8970b-bbee-479d-922b-ab310cd893b3.config
2026-07-26T19:48:14.1383751Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/floci/floci/.git/worktrees/*.path /home/runner/work/_temp/git-credentials-1dd8970b-bbee-479d-922b-ab310cd893b3.config
2026-07-26T19:48:14.1413854Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-07-26T19:48:14.1434950Z /github/runner_temp/git-credentials-1dd8970b-bbee-479d-922b-ab310cd893b3.config
2026-07-26T19:48:14.1441634Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git.path /github/runner_temp/git-credentials-1dd8970b-bbee-479d-922b-ab310cd893b3.config
2026-07-26T19:48:14.1470781Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-26T19:48:14.1491876Z /github/runner_temp/git-credentials-1dd8970b-bbee-479d-922b-ab310cd893b3.config
2026-07-26T19:48:14.1498224Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path /github/runner_temp/git-credentials-1dd8970b-bbee-479d-922b-ab310cd893b3.config
2026-07-26T19:48:14.1529304Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-07-26T19:48:14.1725343Z Removing credentials config '/home/runner/work/_temp/git-credentials-1dd8970b-bbee-479d-922b-ab310cd893b3.config'
2026-07-26T19:48:14.1869474Z Cleaning up orphan processes
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 27. `floci-io__floci__091421214772.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/floci-io__floci__091421214772.txt` (authoritative; read this, not the excerpt)
- **Repository**: `floci-io/floci`
- **Content hash (sha256, first 16)**: `9a5131f768d2768d`
- **Body size**: 500,214 bytes, 3,773 lines
- **Excerpt**: final 120 of 3,773 lines, content-blind

```text
2026-08-01T22:24:38.0678292Z 2026-08-01 22:24:37,220 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-08-01T22:24:38.0678677Z 2026-08-01 22:24:37,220 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-5fddb901 in region us-east-1 (version 1)
2026-08-01T22:24:38.0679020Z 2026-08-01 22:24:37,222 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: LabelParameterVersion
2026-08-01T22:24:38.0679425Z 2026-08-01 22:24:37,222 INFO  [io.git.hec.flo.ser.ssm.SsmService] Labeled parameter /pytest-sdk-test/pytest-5fddb901 version 1 with labels [py-label]
2026-08-01T22:24:38.0679751Z 2026-08-01 22:24:37,224 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-08-01T22:24:38.0680046Z 2026-08-01 22:24:37,224 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-5fddb901
2026-08-01T22:24:38.0680354Z 2026-08-01 22:24:37,230 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-08-01T22:24:38.0680738Z 2026-08-01 22:24:37,230 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-5825bb86 in region us-east-1 (version 1)
2026-08-01T22:24:38.0681066Z 2026-08-01 22:24:37,232 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: GetParameterHistory
2026-08-01T22:24:38.0681487Z 2026-08-01 22:24:37,234 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-08-01T22:24:38.0681933Z 2026-08-01 22:24:37,234 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-5825bb86
2026-08-01T22:24:38.0682260Z 2026-08-01 22:24:37,242 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-08-01T22:24:38.0682648Z 2026-08-01 22:24:37,242 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-ab9d3709 in region us-east-1 (version 1)
2026-08-01T22:24:38.0682958Z 2026-08-01 22:24:37,244 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: GetParameters
2026-08-01T22:24:38.0683279Z 2026-08-01 22:24:37,246 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-08-01T22:24:38.0683577Z 2026-08-01 22:24:37,246 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-ab9d3709
2026-08-01T22:24:38.0683882Z 2026-08-01 22:24:37,253 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-08-01T22:24:38.0684403Z 2026-08-01 22:24:37,253 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-0cfbaa15 in region us-east-1 (version 1)
2026-08-01T22:24:38.0684730Z 2026-08-01 22:24:37,255 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DescribeParameters
2026-08-01T22:24:38.0685050Z 2026-08-01 22:24:37,257 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-08-01T22:24:38.0685343Z 2026-08-01 22:24:37,257 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-0cfbaa15
2026-08-01T22:24:38.0685646Z 2026-08-01 22:24:37,264 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-08-01T22:24:38.0686061Z 2026-08-01 22:24:37,264 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-4a7fc1da/param in region us-east-1 (version 1)
2026-08-01T22:24:38.0686398Z 2026-08-01 22:24:37,266 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: GetParametersByPath
2026-08-01T22:24:38.0686717Z 2026-08-01 22:24:37,268 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-08-01T22:24:38.0687032Z 2026-08-01 22:24:37,268 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-4a7fc1da/param
2026-08-01T22:24:38.0687341Z 2026-08-01 22:24:37,275 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-08-01T22:24:38.0687723Z 2026-08-01 22:24:37,275 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-91e3aa5f in region us-east-1 (version 1)
2026-08-01T22:24:38.0688056Z 2026-08-01 22:24:37,277 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: AddTagsToResource
2026-08-01T22:24:38.0688375Z 2026-08-01 22:24:37,279 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-08-01T22:24:38.0688675Z 2026-08-01 22:24:37,279 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-91e3aa5f
2026-08-01T22:24:38.0688984Z 2026-08-01 22:24:37,287 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-08-01T22:24:38.0689370Z 2026-08-01 22:24:37,287 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-beed444d in region us-east-1 (version 1)
2026-08-01T22:24:38.0689697Z 2026-08-01 22:24:37,289 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: AddTagsToResource
2026-08-01T22:24:38.0690030Z 2026-08-01 22:24:37,291 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: ListTagsForResource
2026-08-01T22:24:38.0690466Z 2026-08-01 22:24:37,293 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-08-01T22:24:38.0690767Z 2026-08-01 22:24:37,293 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-beed444d
2026-08-01T22:24:38.0691075Z 2026-08-01 22:24:37,300 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-08-01T22:24:38.0691460Z 2026-08-01 22:24:37,300 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-0aed4d40 in region us-east-1 (version 1)
2026-08-01T22:24:38.0691928Z 2026-08-01 22:24:37,302 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: AddTagsToResource
2026-08-01T22:24:38.0692284Z 2026-08-01 22:24:37,304 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: RemoveTagsFromResource
2026-08-01T22:24:38.0692625Z 2026-08-01 22:24:37,306 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: ListTagsForResource
2026-08-01T22:24:38.0692946Z 2026-08-01 22:24:37,308 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-08-01T22:24:38.0693365Z 2026-08-01 22:24:37,308 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-0aed4d40
2026-08-01T22:24:38.0693675Z 2026-08-01 22:24:37,315 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-08-01T22:24:38.0694061Z 2026-08-01 22:24:37,315 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-0cd68150 in region us-east-1 (version 1)
2026-08-01T22:24:38.0694376Z 2026-08-01 22:24:37,317 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameter
2026-08-01T22:24:38.0694670Z 2026-08-01 22:24:37,317 INFO  [io.git.hec.flo.ser.ssm.SsmService] Deleted parameter: /pytest-sdk-test/pytest-0cd68150
2026-08-01T22:24:38.0694977Z 2026-08-01 22:24:37,319 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: GetParameter
2026-08-01T22:24:38.0695289Z 2026-08-01 22:24:37,331 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-08-01T22:24:38.0695697Z 2026-08-01 22:24:37,331 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-f9422f21/p1 in region us-east-1 (version 1)
2026-08-01T22:24:38.0696003Z 2026-08-01 22:24:37,333 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: PutParameter
2026-08-01T22:24:38.0696400Z 2026-08-01 22:24:37,333 INFO  [io.git.hec.flo.ser.ssm.SsmService] Put parameter: /pytest-sdk-test/pytest-f9422f21/p2 in region us-east-1 (version 1)
2026-08-01T22:24:38.0696727Z 2026-08-01 22:24:37,335 INFO  [io.git.hec.flo.cor.com.AwsJson11Controller] AwsJson11Controller ssm action: DeleteParameters
2026-08-01T22:24:38.0793442Z Post job cleanup.
2026-08-01T22:24:38.3125505Z ##[group]Generating build summary
2026-08-01T22:24:38.3680700Z exporting build record to /home/runner/work/_temp/docker-actions-toolkit-Ynyfqx/export
2026-08-01T22:24:38.4623979Z [command]/usr/bin/docker buildx history export --builder builder-28cf0dfa-a17c-449e-8037-96a471f7dfe4 --output /home/runner/work/_temp/docker-actions-toolkit-Ynyfqx/export/floci-io~floci~KROKSB.dockerbuild kroksblyuqbl1p8kp42e7vngf --finalize
2026-08-01T22:24:38.6134680Z Build record written to /home/runner/work/_temp/docker-actions-toolkit-Ynyfqx/export/floci-io~floci~KROKSB.dockerbuild (39.99 KB)
2026-08-01T22:24:38.6136950Z Uploading floci-io~floci~KROKSB.dockerbuild as an artifact
2026-08-01T22:24:38.6140459Z Artifact name is valid!
2026-08-01T22:24:38.6141124Z Root directory input is valid!
2026-08-01T22:24:38.7819648Z Uploading artifact: floci-io~floci~KROKSB.dockerbuild
2026-08-01T22:24:38.7855021Z Beginning upload of artifact content to blob storage
2026-08-01T22:24:38.8998355Z Uploaded bytes 40945
2026-08-01T22:24:38.9280727Z Finished uploading artifact content to blob storage!
2026-08-01T22:24:38.9281285Z SHA256 digest of uploaded artifact is 56643115cb8e91a99e3a2cbf6636836b05d48b76e6a4f9649f94102db746712f
2026-08-01T22:24:38.9281896Z Finalizing artifact upload
2026-08-01T22:24:39.1410758Z Artifact floci-io~floci~KROKSB.dockerbuild successfully finalized. Artifact ID 8824901619
2026-08-01T22:24:39.1412292Z Artifact download URL: https://github.com/floci-io/floci/actions/runs/30268957061/artifacts/8824901619
2026-08-01T22:24:39.1434371Z Writing summary
2026-08-01T22:24:39.1446672Z ##[endgroup]
2026-08-01T22:24:39.1447159Z ##[group]Removing temp folder /home/runner/work/_temp/docker-actions-toolkit-tnKb9w
2026-08-01T22:24:39.1449343Z ##[endgroup]
2026-08-01T22:24:39.1449783Z ##[group]Post cache
2026-08-01T22:24:39.1450637Z State not set
2026-08-01T22:24:39.1450976Z ##[endgroup]
2026-08-01T22:24:39.1603555Z Post job cleanup.
2026-08-01T22:24:39.3460859Z ##[group]Removing builder
2026-08-01T22:24:39.4265335Z [command]/usr/bin/docker buildx rm builder-28cf0dfa-a17c-449e-8037-96a471f7dfe4
2026-08-01T22:24:39.6791495Z builder-28cf0dfa-a17c-449e-8037-96a471f7dfe4 removed
2026-08-01T22:24:39.6819862Z ##[endgroup]
2026-08-01T22:24:39.6820239Z ##[group]Cleaning up certificates
2026-08-01T22:24:39.6822958Z ##[endgroup]
2026-08-01T22:24:39.6824078Z ##[group]Post cache
2026-08-01T22:24:39.6825262Z State not set
2026-08-01T22:24:39.6826386Z ##[endgroup]
2026-08-01T22:24:39.6975916Z Post job cleanup.
2026-08-01T22:24:39.7656743Z [command]/usr/bin/git version
2026-08-01T22:24:39.7696106Z git version 2.54.0
2026-08-01T22:24:39.7728496Z Temporarily overriding HOME='/home/runner/work/_temp/112975b9-5077-459f-912b-cce0b74cafb9' before making global git config changes
2026-08-01T22:24:39.7729316Z Adding repository directory to the temporary git global config as a safe directory
2026-08-01T22:24:39.7733134Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/floci/floci
2026-08-01T22:24:39.7763892Z Removing SSH command configuration
2026-08-01T22:24:39.7770223Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-08-01T22:24:39.7801386Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-08-01T22:24:39.7998951Z Removing HTTP extra header
2026-08-01T22:24:39.8004334Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-08-01T22:24:39.8038235Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-08-01T22:24:39.8232742Z Removing includeIf entries pointing to credentials config files
2026-08-01T22:24:39.8238066Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-08-01T22:24:39.8262629Z includeif.gitdir:/home/runner/work/floci/floci/.git.path
2026-08-01T22:24:39.8263072Z includeif.gitdir:/home/runner/work/floci/floci/.git/worktrees/*.path
2026-08-01T22:24:39.8263445Z includeif.gitdir:/github/workspace/.git.path
2026-08-01T22:24:39.8263780Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-08-01T22:24:39.8270189Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/floci/floci/.git.path
2026-08-01T22:24:39.8291818Z /home/runner/work/_temp/git-credentials-1afa6648-765d-4f49-93c6-2927f59deeca.config
2026-08-01T22:24:39.8300885Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/floci/floci/.git.path /home/runner/work/_temp/git-credentials-1afa6648-765d-4f49-93c6-2927f59deeca.config
2026-08-01T22:24:39.8332246Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/floci/floci/.git/worktrees/*.path
2026-08-01T22:24:39.8352901Z /home/runner/work/_temp/git-credentials-1afa6648-765d-4f49-93c6-2927f59deeca.config
2026-08-01T22:24:39.8367373Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/floci/floci/.git/worktrees/*.path /home/runner/work/_temp/git-credentials-1afa6648-765d-4f49-93c6-2927f59deeca.config
2026-08-01T22:24:39.8397515Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-08-01T22:24:39.8418934Z /github/runner_temp/git-credentials-1afa6648-765d-4f49-93c6-2927f59deeca.config
2026-08-01T22:24:39.8425328Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git.path /github/runner_temp/git-credentials-1afa6648-765d-4f49-93c6-2927f59deeca.config
2026-08-01T22:24:39.8455867Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-08-01T22:24:39.8478058Z /github/runner_temp/git-credentials-1afa6648-765d-4f49-93c6-2927f59deeca.config
2026-08-01T22:24:39.8485033Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path /github/runner_temp/git-credentials-1afa6648-765d-4f49-93c6-2927f59deeca.config
2026-08-01T22:24:39.8515533Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-08-01T22:24:39.8708876Z Removing credentials config '/home/runner/work/_temp/git-credentials-1afa6648-765d-4f49-93c6-2927f59deeca.config'
2026-08-01T22:24:39.8847652Z Cleaning up orphan processes
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 28. `grobidOrg__grobid__082786414435.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/grobidOrg__grobid__082786414435.txt` (authoritative; read this, not the excerpt)
- **Repository**: `grobidOrg/grobid`
- **Content hash (sha256, first 16)**: `ed8a3d8ff9379ed8`
- **Body size**: 1,215,976 bytes, 7,432 lines
- **Excerpt**: final 120 of 7,432 lines, content-blind

```text
2026-06-22T18:20:28.9883467Z TextUtilitiesTest:1 | testDephynizationHard_withSpaces (0.001s)
2026-06-22T18:20:28.9884113Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_sequence3_shouldReturnFalse (0.0s)
2026-06-22T18:20:28.9884689Z TextUtilitiesTest:1 | testFormat4Digits (0.001s)
2026-06-22T18:20:28.9885131Z TextUtilitiesTest:1 | testHTMLEncode_partial (0.0s)
2026-06-22T18:20:28.9885697Z TextUtilitiesTest:1 | testDephynization_falseTruncation_shouldReturnSameString (0.001s)
2026-06-22T18:20:28.9886412Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_trickySequence5_shouldReturnFalse (0.0s)
2026-06-22T18:20:28.9886985Z TextUtilitiesTest:1 | testSuffixes (0.001s)
2026-06-22T18:20:28.9888057Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_trickySequence8_shouldReturnTrue (0.0s)
2026-06-22T18:20:28.9888838Z TextUtilitiesTest:1 | testNormaliseText_collapsesNonBreakingSpace_issue849 (0.001s)
2026-06-22T18:20:28.9889547Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_withSpaceBefore_shouldReturnTrue (0.0s)
2026-06-22T18:20:28.9890263Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_sequence2_shouldReturnFalse (0.001s)
2026-06-22T18:20:29.2819457Z grobid-core/src/test/java/org/grobid/core/utilities/TextUtilitiesTest.java:665 | java.lang.AssertionError:  (0.009s)
2026-06-22T18:20:29.2820216Z TextUtilitiesTest:1 | testDephynizationHard_citation (0.0s)
2026-06-22T18:20:29.2820813Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_standard_shouldReturnTrue (0.001s)
2026-06-22T18:20:29.2821427Z TextUtilitiesTest:1 | testGetFirstToken_spaceParenthesis (0.0s)
2026-06-22T18:20:29.2821960Z TextUtilitiesTest:1 | testMatchTokenAndString_twoElements (0.005s)
2026-06-22T18:20:29.2822650Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_usualWordWithSpace_shouldReturnFalse (0.001s)
2026-06-22T18:20:29.2823399Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_falseFriend3_shouldReturnTrue (0.0s)
2026-06-22T18:20:29.2824539Z TextUtilitiesTest:1 | testDephynization_withSpaces (0.001s)
2026-06-22T18:20:29.2825156Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_trickySequence4_shouldReturnFalse (0.0s)
2026-06-22T18:20:29.2825761Z TextUtilitiesTest:1 | testMatchTokenAndString (0.0s)
2026-06-22T18:20:29.2826201Z TextUtilitiesTest:1 | testOrcidPattern (0.001s)
2026-06-22T18:20:29.2826782Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_trickySequence7_shouldReturnTrue (0.001s)
2026-06-22T18:20:29.2827555Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_usualWordWith2Space_shouldReturnFalse (0.0s)
2026-06-22T18:20:29.2828441Z TextUtilitiesTest:1 | testIsAllUpperCaseOrDigitOrDot (0.0s)
2026-06-22T18:20:29.2829031Z TextUtilitiesTest:1 | testMatchTokenAndString_twoElementsWithEqualValue2 (0.002s)
2026-06-22T18:20:29.2829699Z TextUtilitiesTest:1 | testMatchTokenAndString_twoElementsWithEqualValue3 (0.002s)
2026-06-22T18:20:29.2830400Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_withSpacesBefore_shouldReturnTrue (0.001s)
2026-06-22T18:20:29.2831101Z TextUtilitiesTest:1 | testMatchTokenAndString_twoElementsWithEqualValue (0.0s)
2026-06-22T18:20:29.2831777Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_falseFriend2_shouldReturnTrue (0.001s)
2026-06-22T18:20:29.2832498Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_trickySequence3_shouldReturnFalse (0.0s)
2026-06-22T18:20:29.2833183Z TextUtilitiesTest:1 | testDephynization_withDigits_shouldNotDephypenize (0.0s)
2026-06-22T18:20:29.2833859Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_withSpacesAfter_shouldReturnTrue (0.0s)
2026-06-22T18:20:29.2834464Z TextUtilitiesTest:1 | testHTMLEncode_complete (0.0s)
2026-06-22T18:20:29.2835035Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_usualWord_shouldReturnFalse (0.001s)
2026-06-22T18:20:29.2835606Z TextUtilitiesTest:1 | testFormat2Digits (0.0s)
2026-06-22T18:20:29.2836161Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_sequence_shouldReturnFalse (0.001s)
2026-06-22T18:20:29.2836791Z TextUtilitiesTest:1 | testDephynizationHard_withoutSpaces (0.0s)
2026-06-22T18:20:29.2837415Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_withSpaceAfter_shouldReturnTrue (0.0s)
2026-06-22T18:20:29.2838455Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_trickySequence2_shouldReturnFalse (0.0s)
2026-06-22T18:20:29.2839187Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_falseFriend1_shouldReturnTrue (0.0s)
2026-06-22T18:20:29.2839788Z TextUtilitiesTest:1 | testDephynization_citation (0.001s)
2026-06-22T18:20:29.2840230Z TextUtilitiesTest:1 | testWordShape (0.0s)
2026-06-22T18:20:29.2840680Z TextUtilitiesTest:1 | testDephynization_withoutSpaces (0.001s)
2026-06-22T18:20:29.2843186Z TextUtilitiesTest:1 | testPrefix (0.0s)
2026-06-22T18:20:29.2844028Z TextUtilitiesTest:1 | testDehyphenizationWithLayoutTokens (0.0s)
2026-06-22T18:20:29.2844646Z TextUtilitiesTest:1 | testClean_stillExpandsTypographicLigatures_issue728 (0.001s)
2026-06-22T18:20:29.2845314Z TextUtilitiesTest:1 | testDephynizationHard_withDigits_shouldNotDephypenize (0.0s)
2026-06-22T18:20:29.2845907Z TextUtilitiesTest:1 | testGetLastToken_spaceParenthesis (0.0s)
2026-06-22T18:20:29.2846534Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_trickySequence1_shouldReturnFalse (0.001s)
2026-06-22T18:20:29.2847280Z TextUtilitiesTest:1 | testDoesRequireDehypenisation_trickySequence6_shouldReturnFalse (0.0s)
2026-06-22T18:20:29.2848238Z TextUtilitiesTest:1 | testDephynization_FalseTruncation_shouldReturnSameString (0.001s)
2026-06-22T18:20:29.2849086Z UnicodeUtilTest:1 | testNormaliseToken (0.0s)
2026-06-22T18:20:29.2849750Z UtilitiesTest:1 | testStringToBooleanTrue (0.013s)
2026-06-22T18:20:29.2850243Z UtilitiesTest:1 | testConvertStringOffsetToTokenOffset (0.365s)
2026-06-22T18:20:29.2863403Z UtilitiesTest:1 | testStringToBooleanBlank (0.001s)
2026-06-22T18:20:29.2864018Z UtilitiesTest:1 | testStringToBooleanFalse (0.001s)
2026-06-22T18:20:29.2864466Z UtilitiesTest:1 | testStringToBooleanTrue2 (0.0s)
2026-06-22T18:20:29.2865200Z UtilitiesTest:1 | testMergePositionsOverlap (0.006s)
2026-06-22T18:20:29.2865638Z UtilitiesTest:1 | testMergePositions1 (0.0s)
2026-06-22T18:20:29.2866048Z UtilitiesTest:1 | testMergePositions2 (0.001s)
2026-06-22T18:20:29.2866469Z UtilitiesTest:1 | testStringToBooleanBlank2 (0.0s)
2026-06-22T18:20:29.2866909Z UtilitiesTest:1 | testStringToBooleanFalse2 (0.0s)
2026-06-22T18:20:29.2867347Z UtilitiesTest:1 | testStringToBooleanFalse3 (0.001s)
2026-06-22T18:20:29.2868309Z GrobidTimerTest:1 | testGrobidTimerBoolConstructorTrue (0.003s)
2026-06-22T18:20:29.2868838Z GrobidTimerTest:1 | testGrobidTimerEmptyConstructor (0.001s)
2026-06-22T18:20:29.2869353Z GrobidTimerTest:1 | testGrobidTimerBoolConstructorFalse (0.0s)
2026-06-22T18:20:29.2900860Z CntManagerImplTest:1 | testGetAllCounters (0.745s)
2026-06-22T18:20:29.2901558Z CntManagerImplTest:1 | getCounters_shouldWork (0.001s)
2026-06-22T18:20:29.2902132Z CntManagerImplTest:1 | getCounterEnclosingClass_NoEnclosingClass_shouldWork (0.0s)
2026-06-22T18:20:29.2902704Z CntManagerImplTest:1 | getCounter_shouldWork (0.001s)
2026-06-22T18:20:29.2903208Z CntManagerImplTest:1 | testGetAllCounters_checkGroupName (0.004s)
2026-06-22T18:20:29.2903701Z CntManagerImplTest:1 | testGetAllCounters2 (0.001s)
2026-06-22T18:20:29.2904239Z CntManagerImplTest:1 | getCounterEnclosingClass_EnclosingClass_sholdWork (0.0s)
2026-06-22T18:20:29.2904791Z CntManagerImplTest:1 | testCountSingleGroup (0.001s)
2026-06-22T18:20:29.2905230Z CntManagerImplTest:1 | testCnt_withClass (0.001s)
2026-06-22T18:20:29.2905685Z CntManagerImplTest:1 | testCnt_withExplicitValues (0.0s)
2026-06-22T18:20:29.2906439Z TestCitationsVisualizer:1 | testJSONAnnotationStructure (27.139s)
2026-06-22T18:20:29.2906979Z TestCitationsVisualizer:1 | testJSONAnnotationEscaping (0.94s)
2026-06-22T18:20:30.1171174Z Found and parsed 80 test report files.
2026-06-22T18:20:30.1180574Z ℹ️ Posting with conclusion 'failure' to refs/heads/bugfix/fix-671 (sha: 83944a94d6c5eff253eaa77ea3cb0ce5c45ad2fa)
2026-06-22T18:20:30.1181357Z ##[endgroup]
2026-06-22T18:20:30.1181805Z ##[group]🚀 Publish results
2026-06-22T18:20:30.1183642Z ℹ️ - JUnit Test Report - 565 tests run, 519 passed, 43 skipped, 3 failed.
2026-06-22T18:20:30.1184346Z    🧪 - grobid-core/src/test/kotlin/org/grobid/core/data/BiblioItemTest.kt | java.lang.AssertionError: 
2026-06-22T18:20:30.1185097Z    🧪 - grobid-core/src/test/kotlin/org/grobid/core/data/BiblioItemTest.kt | java.lang.AssertionError: 
2026-06-22T18:20:30.1185920Z    🧪 - grobid-core/src/test/java/org/grobid/core/utilities/TextUtilitiesTest.java | java.lang.AssertionError: 
2026-06-22T18:20:30.1192902Z ℹ️ - JUnit Test Report - Creating check (Annotations: 3)
2026-06-22T18:20:30.3489580Z ##[error]❌ Failed to create checks using the provided token. (HttpError: Resource not accessible by integration - https://docs.github.com/rest/checks/runs#create-a-check-run)
2026-06-22T18:20:30.3493405Z ##[warning]⚠️ This usually indicates insufficient permissions. More details: https://github.com/mikepenz/action-junit-report/issues/23
2026-06-22T18:20:30.3519247Z ##[endgroup]
2026-06-22T18:20:30.3944891Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-22T18:20:30.3946068Z Post job cleanup.
2026-06-22T18:20:30.5921046Z In post-action step
2026-06-22T18:20:30.5929822Z Cache is read-only: will not save state for use in subsequent builds.
2026-06-22T18:20:30.5934529Z Generating Job Summary
2026-06-22T18:20:30.5950848Z Completed post-action step
2026-06-22T18:20:30.6086490Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-22T18:20:30.6088489Z Post job cleanup.
2026-06-22T18:20:30.7190832Z (node:6080) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-06-22T18:20:30.7191504Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-06-22T18:20:30.7325858Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-22T18:20:30.7327040Z Post job cleanup.
2026-06-22T18:20:30.8007857Z [command]/usr/bin/git version
2026-06-22T18:20:30.8043222Z git version 2.54.0
2026-06-22T18:20:30.8076185Z Temporarily overriding HOME='/home/runner/work/_temp/80258cba-32e5-45d0-b8f6-be5eaa32207e' before making global git config changes
2026-06-22T18:20:30.8076929Z Adding repository directory to the temporary git global config as a safe directory
2026-06-22T18:20:30.8080647Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/grobid/grobid
2026-06-22T18:20:30.8116700Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-06-22T18:20:30.8145710Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-06-22T18:20:30.8345759Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-06-22T18:20:30.8366098Z http.https://github.com/.extraheader
2026-06-22T18:20:30.8377459Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-06-22T18:20:30.8405627Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-06-22T18:20:30.8609950Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-06-22T18:20:30.8639312Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-06-22T18:20:30.8954865Z Cleaning up orphan processes
2026-06-22T18:20:30.9256248Z Terminate orphan process: pid (2331) (java)
2026-06-22T18:20:30.9276865Z Terminate orphan process: pid (2620) (java)
2026-06-22T18:20:30.9306745Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/checkout@v4, actions/setup-java@v4, gradle/actions/setup-gradle@v4, mikepenz/action-junit-report@v4. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 29. `jline__jline3__086920871447.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/jline__jline3__086920871447.txt` (authoritative; read this, not the excerpt)
- **Repository**: `jline/jline3`
- **Content hash (sha256, first 16)**: `626d425848185eb3`
- **Body size**: 42,518 bytes, 512 lines
- **Excerpt**: final 120 of 512 lines, content-blind

```text
2026-07-13T20:01:20.3352393Z [INFO] 
2026-07-13T20:01:20.3359393Z [INFO] --- enforcer:3.6.3:enforce (enforce-maven) @ jline-terminal ---
2026-07-13T20:01:20.3393554Z [INFO] 
2026-07-13T20:01:20.3403715Z [INFO] --- spotless:3.8.0:check (default) @ jline-terminal ---
2026-07-13T20:01:20.3478454Z [INFO] Index file does not exist. Fallback to an empty index
2026-07-13T20:01:22.2360197Z [INFO] Spotless.Java is keeping 138 files clean - 0 needs changes to be clean, 138 were already clean, 0 were skipped because caching determined they were already clean
2026-07-13T20:01:22.3411568Z [INFO] Sorting file /tmp/pom692479990646994411.xml
2026-07-13T20:01:22.3464309Z [INFO] Pom file is already sorted, exiting
2026-07-13T20:01:22.3465268Z [INFO] Spotless.Pom is keeping 1 files clean - 0 needs changes to be clean, 1 were already clean, 0 were skipped because caching determined they were already clean
2026-07-13T20:01:22.3473556Z [INFO] 
2026-07-13T20:01:22.3473994Z [INFO] --- resources:3.5.0:resources (default-resources) @ jline-terminal ---
2026-07-13T20:01:22.3503576Z [INFO] Copying 24 resources from src/main/resources to target/classes
2026-07-13T20:01:22.3533628Z [INFO] 
2026-07-13T20:01:22.3563819Z [INFO] --- compiler:3.15.0:compile (default-compile) @ jline-terminal ---
2026-07-13T20:01:22.3794099Z [INFO] Recompiling the module because of changed dependency.
2026-07-13T20:01:22.3794447Z [INFO] Compiling 93 source files with javac [forked debug release 11 module-path] to target/classes
2026-07-13T20:01:24.0482917Z [INFO] -------------------------------------------------------------
2026-07-13T20:01:24.0483669Z [WARNING] COMPILATION WARNING : 
2026-07-13T20:01:24.0484040Z [INFO] -------------------------------------------------------------
2026-07-13T20:01:24.0485108Z [WARNING] /home/runner/work/jline3/jline3/terminal/src/main/java/org/jline/utils/ExecHelper.java:[82,29] [try] auto-closeable resource out is never referenced in body of corresponding try statement
2026-07-13T20:01:24.0485865Z [INFO] 1 warning
2026-07-13T20:01:24.0486340Z [INFO] -------------------------------------------------------------
2026-07-13T20:01:24.0486767Z [INFO] -------------------------------------------------------------
2026-07-13T20:01:24.0487048Z [ERROR] COMPILATION ERROR : 
2026-07-13T20:01:24.0487306Z [INFO] -------------------------------------------------------------
2026-07-13T20:01:24.0487598Z [ERROR] error: warnings found and -Werror specified
2026-07-13T20:01:24.0487849Z [INFO] 1 error
2026-07-13T20:01:24.0488081Z [INFO] -------------------------------------------------------------
2026-07-13T20:01:24.0488461Z [INFO] ------------------------------------------------------------------------
2026-07-13T20:01:24.0488762Z [INFO] Reactor Summary for JLine 0.1.0-1-SNAPSHOT:
2026-07-13T20:01:24.0489015Z [INFO] 
2026-07-13T20:01:24.0490585Z [INFO] JLine .............................................. SUCCESS [  0.965 s]
2026-07-13T20:01:24.0490985Z [INFO] JLine Native Library ............................... SUCCESS [  3.448 s]
2026-07-13T20:01:24.0491362Z [INFO] JLine Terminal ..................................... FAILURE [  3.726 s]
2026-07-13T20:01:24.0491661Z [INFO] JLine FFM Terminal ................................. SKIPPED
2026-07-13T20:01:24.0491906Z [INFO] JLine JNI Terminal ................................. SKIPPED
2026-07-13T20:01:24.0492366Z [INFO] JLine Reader ....................................... SKIPPED
2026-07-13T20:01:24.0497001Z [INFO] JLine Shell ........................................ SKIPPED
2026-07-13T20:01:24.0503713Z [INFO] JLine Style ........................................ SKIPPED
2026-07-13T20:01:24.0505105Z [INFO] JLine Builtins ..................................... SKIPPED
2026-07-13T20:01:24.0505439Z [INFO] JLine Console UI (Deprecated) ...................... SKIPPED
2026-07-13T20:01:24.0505756Z [INFO] JLine Prompt ....................................... SKIPPED
2026-07-13T20:01:24.0505963Z [INFO] JLine Console ...................................... SKIPPED
2026-07-13T20:01:24.0506173Z [INFO] JLine Picocli ...................................... SKIPPED
2026-07-13T20:01:24.0506376Z [INFO] JLine Groovy ....................................... SKIPPED
2026-07-13T20:01:24.0506577Z [INFO] JLine Remote SSH ................................... SKIPPED
2026-07-13T20:01:24.0506861Z [INFO] JLine Remote Telnet ................................ SKIPPED
2026-07-13T20:01:24.0507173Z [INFO] JLine Demo ......................................... SKIPPED
2026-07-13T20:01:24.0507485Z [INFO] JLine Native Demo .................................. SKIPPED
2026-07-13T20:01:24.0507794Z [INFO] Jansi Core ......................................... SKIPPED
2026-07-13T20:01:24.0508099Z [INFO] JLine Bundle ....................................... SKIPPED
2026-07-13T20:01:24.0508411Z [INFO] Jansi Bundle ....................................... SKIPPED
2026-07-13T20:01:24.0508740Z [INFO] ------------------------------------------------------------------------
2026-07-13T20:01:24.0508947Z [INFO] BUILD FAILURE
2026-07-13T20:01:24.0509115Z [INFO] ------------------------------------------------------------------------
2026-07-13T20:01:24.0509320Z [INFO] Total time:  8.279 s
2026-07-13T20:01:24.0509460Z [INFO] Finished at: 2026-07-13T20:01:24Z
2026-07-13T20:01:24.0509647Z [INFO] ------------------------------------------------------------------------
2026-07-13T20:01:24.0509866Z [INFO] Nisse property inliner cleanup of 21 inlined POMs
2026-07-13T20:01:24.0510038Z [INFO] Njord session closed
2026-07-13T20:01:24.0510381Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.15.0:compile (default-compile) on project jline-terminal: Compilation failure
2026-07-13T20:01:24.0510754Z [ERROR] error: warnings found and -Werror specified
2026-07-13T20:01:24.0511041Z [ERROR] 
2026-07-13T20:01:24.0511145Z [ERROR] -> [Help 1]
2026-07-13T20:01:24.0511258Z [ERROR] 
2026-07-13T20:01:24.0511426Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-07-13T20:01:24.0511739Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-07-13T20:01:24.0511919Z [ERROR] 
2026-07-13T20:01:24.0512137Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-07-13T20:01:24.0512472Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
2026-07-13T20:01:24.0512690Z [ERROR] 
2026-07-13T20:01:24.0512934Z [ERROR] After correcting the problems, you can resume the build with the command
2026-07-13T20:01:24.0513290Z [ERROR]   mvn <args> -rf :jline-terminal
2026-07-13T20:01:24.0627144Z Error: exit status 1
2026-07-13T20:01:24.0627397Z Usage:
2026-07-13T20:01:24.0627576Z   mvx mvn [args...] [flags]
2026-07-13T20:01:24.0627720Z 
2026-07-13T20:01:24.0627812Z Flags:
2026-07-13T20:01:24.0628020Z   -h, --help   help for mvn
2026-07-13T20:01:24.0628158Z 
2026-07-13T20:01:24.0628237Z Global Flags:
2026-07-13T20:01:24.0628440Z   -q, --quiet     quiet output (errors only)
2026-07-13T20:01:24.0628704Z   -v, --verbose   verbose output
2026-07-13T20:01:24.0628859Z 
2026-07-13T20:01:24.0628954Z Error: exit status 1
2026-07-13T20:01:24.0642350Z ##[error]Process completed with exit code 1.
2026-07-13T20:01:24.0715365Z Post job cleanup.
2026-07-13T20:01:24.1514611Z Post job cleanup.
2026-07-13T20:01:24.2014963Z [command]/usr/bin/git version
2026-07-13T20:01:24.2036133Z git version 2.54.0
2026-07-13T20:01:24.2054955Z Temporarily overriding HOME='/home/runner/work/_temp/1c399c9b-8bcb-48d8-99f5-662e0d7f19f1' before making global git config changes
2026-07-13T20:01:24.2055365Z Adding repository directory to the temporary git global config as a safe directory
2026-07-13T20:01:24.2061986Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/jline3/jline3
2026-07-13T20:01:24.2077123Z Removing SSH command configuration
2026-07-13T20:01:24.2080259Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-07-13T20:01:24.2096486Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-07-13T20:01:24.2195374Z Removing HTTP extra header
2026-07-13T20:01:24.2198795Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-13T20:01:24.2214217Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-07-13T20:01:24.2309599Z Removing includeIf entries pointing to credentials config files
2026-07-13T20:01:24.2314797Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-13T20:01:24.2326890Z includeif.gitdir:/home/runner/work/jline3/jline3/.git.path
2026-07-13T20:01:24.2327347Z includeif.gitdir:/home/runner/work/jline3/jline3/.git/worktrees/*.path
2026-07-13T20:01:24.2327845Z includeif.gitdir:/github/workspace/.git.path
2026-07-13T20:01:24.2328201Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-13T20:01:24.2341082Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/jline3/jline3/.git.path
2026-07-13T20:01:24.2342946Z /home/runner/work/_temp/git-credentials-e6264e5a-9fd4-410e-bd61-c796d3ad323e.config
2026-07-13T20:01:24.2348934Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/jline3/jline3/.git.path /home/runner/work/_temp/git-credentials-e6264e5a-9fd4-410e-bd61-c796d3ad323e.config
2026-07-13T20:01:24.2364515Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/jline3/jline3/.git/worktrees/*.path
2026-07-13T20:01:24.2374417Z /home/runner/work/_temp/git-credentials-e6264e5a-9fd4-410e-bd61-c796d3ad323e.config
2026-07-13T20:01:24.2378856Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/jline3/jline3/.git/worktrees/*.path /home/runner/work/_temp/git-credentials-e6264e5a-9fd4-410e-bd61-c796d3ad323e.config
2026-07-13T20:01:24.2392750Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-07-13T20:01:24.2401927Z /github/runner_temp/git-credentials-e6264e5a-9fd4-410e-bd61-c796d3ad323e.config
2026-07-13T20:01:24.2405268Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git.path /github/runner_temp/git-credentials-e6264e5a-9fd4-410e-bd61-c796d3ad323e.config
2026-07-13T20:01:24.2417887Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-13T20:01:24.2426502Z /github/runner_temp/git-credentials-e6264e5a-9fd4-410e-bd61-c796d3ad323e.config
2026-07-13T20:01:24.2430109Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path /github/runner_temp/git-credentials-e6264e5a-9fd4-410e-bd61-c796d3ad323e.config
2026-07-13T20:01:24.2443567Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-07-13T20:01:24.2535748Z Removing credentials config '/home/runner/work/_temp/git-credentials-e6264e5a-9fd4-410e-bd61-c796d3ad323e.config'
2026-07-13T20:01:24.2631461Z Cleaning up orphan processes
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 30. `nitrite__nitrite-java__090043799546.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/nitrite__nitrite-java__090043799546.txt` (authoritative; read this, not the excerpt)
- **Repository**: `nitrite/nitrite-java`
- **Content hash (sha256, first 16)**: `1defb841c8c8c0d9`
- **Body size**: 140,439 bytes, 1,286 lines
- **Excerpt**: final 120 of 1,286 lines, content-blind

```text
2026-07-27T16:44:58.4719780Z [INFO] Running org.dizitart.nitrite.test.transaction.TransactionTest
2026-07-27T16:44:58.5600997Z [INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.103 s -- in org.dizitart.nitrite.test.transaction.TransactionTest
2026-07-27T16:44:58.5602495Z [INFO] Running org.dizitart.nitrite.test.compat.CompatTest
2026-07-27T16:44:58.6239972Z [INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.072 s -- in org.dizitart.nitrite.test.compat.CompatTest
2026-07-27T16:44:58.6241474Z [INFO] Running org.dizitart.nitrite.test.migration.MigrationTest
2026-07-27T16:44:58.7198099Z [INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.089 s -- in org.dizitart.nitrite.test.migration.MigrationTest
2026-07-27T16:44:58.7219282Z [INFO] Running org.dizitart.nitrite.test.repository.RepositoryTest
2026-07-27T16:44:58.7690174Z [INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.050 s -- in org.dizitart.nitrite.test.repository.RepositoryTest
2026-07-27T16:44:58.7934016Z [INFO] 
2026-07-27T16:44:58.7934349Z [INFO] Results:
2026-07-27T16:44:58.7934662Z [INFO] 
2026-07-27T16:44:58.7939659Z [INFO] Tests run: 7, Failures: 0, Errors: 0, Skipped: 0
2026-07-27T16:44:58.7940198Z [INFO] 
2026-07-27T16:44:58.7976621Z [INFO] 
2026-07-27T16:44:58.7977410Z [INFO] --- native:1.1.6:test (native-test) @ nitrite-native-tests ---
2026-07-27T16:44:58.8076138Z [INFO] Using configuration from maven-surefire-plugin, execution id "default-test"
2026-07-27T16:44:58.8127727Z [INFO] ====================
2026-07-27T16:44:58.8128622Z [INFO] Initializing project: Nitrite Native Tests
2026-07-27T16:44:58.8129323Z [INFO] ====================
2026-07-27T16:44:58.8142133Z [WARNING] No jdk toolchain configuration found
2026-07-27T16:44:58.8160142Z [INFO] Found GraalVM installation from GRAALVM_HOME variable.
2026-07-27T16:44:58.9109966Z [INFO] Downloaded GraalVM reachability metadata repository from file:/home/runner/.m2/repository/org/graalvm/buildtools/graalvm-reachability-metadata/1.1.6/graalvm-reachability-metadata-1.1.6-repository.zip
2026-07-27T16:44:59.3034070Z [INFO] Using GraalVM reachability metadata repository version 1.0.7
2026-07-27T16:44:59.3317662Z [INFO] [graalvm reachability metadata repository for org.slf4j:slf4j-api:2.0.18]: Configuration directory not found. Trying latest version.
2026-07-27T16:44:59.3340435Z [INFO] [graalvm reachability metadata repository for org.slf4j:slf4j-api:2.0.18]: Configuration directory is org.slf4j/slf4j-api/1.7.36
2026-07-27T16:44:59.3359854Z [INFO] [graalvm reachability metadata repository for commons-codec:commons-codec:1.22.0]: Configuration directory is commons-codec/commons-codec/1.10
2026-07-27T16:44:59.3490541Z [INFO] [graalvm reachability metadata repository for org.junit.jupiter:junit-jupiter-api:6.0.0]: Configuration directory not found. Trying latest version.
2026-07-27T16:44:59.3492475Z [INFO] [graalvm reachability metadata repository for org.junit.jupiter:junit-jupiter-api:6.0.0]: Configuration directory is org.junit.jupiter/junit-jupiter-api/5.8.2
2026-07-27T16:44:59.3494295Z [INFO] [graalvm reachability metadata repository for org.opentest4j:opentest4j:1.3.0]: Configuration directory is org.opentest4j/opentest4j/1.2.0
2026-07-27T16:44:59.3499184Z [INFO] [graalvm reachability metadata repository for org.junit.platform:junit-platform-commons:6.0.0]: Configuration directory not found. Trying latest version.
2026-07-27T16:44:59.3501096Z [INFO] [graalvm reachability metadata repository for org.junit.platform:junit-platform-commons:6.0.0]: Configuration directory is org.junit.platform/junit-platform-commons/1.8.2
2026-07-27T16:44:59.3503126Z [INFO] [graalvm reachability metadata repository for org.apiguardian:apiguardian-api:1.1.2]: Configuration directory is org.apiguardian/apiguardian-api/1.1.2
2026-07-27T16:44:59.3507047Z [INFO] [graalvm reachability metadata repository for org.jspecify:jspecify:1.0.0]: Configuration directory is org.jspecify/jspecify/1.0.0
2026-07-27T16:44:59.3508999Z [INFO] [graalvm reachability metadata repository for org.junit.jupiter:junit-jupiter-engine:6.0.0]: Configuration directory is org.junit.jupiter/junit-jupiter-engine/5.8.2
2026-07-27T16:44:59.3528518Z [INFO] [graalvm reachability metadata repository for org.junit.platform:junit-platform-engine:6.0.0]: Configuration directory not found. Trying latest version.
2026-07-27T16:44:59.3530546Z [INFO] [graalvm reachability metadata repository for org.junit.platform:junit-platform-engine:6.0.0]: Configuration directory is org.junit.platform/junit-platform-engine/1.10.4
2026-07-27T16:44:59.3532470Z [INFO] [graalvm reachability metadata repository for org.junit.platform:junit-platform-launcher:6.0.0]: Configuration directory is org.junit.platform/junit-platform-launcher/1.9.2
2026-07-27T16:44:59.3537204Z [INFO] [graalvm reachability metadata repository for org.junit.platform:junit-platform-launcher:6.0.0]: Configuration directory is org.junit.platform/junit-platform-reporting/1.9.2
2026-07-27T16:44:59.5919772Z [INFO] ------------------------------------------------------------------------
2026-07-27T16:44:59.5920546Z [INFO] BUILD FAILURE
2026-07-27T16:44:59.5921033Z [INFO] ------------------------------------------------------------------------
2026-07-27T16:44:59.5927707Z [INFO] Total time:  4.734 s
2026-07-27T16:44:59.5959513Z [INFO] Finished at: 2026-07-27T16:44:59Z
2026-07-27T16:44:59.5980351Z [INFO] ------------------------------------------------------------------------
2026-07-27T16:44:59.5983071Z [ERROR] Failed to execute goal org.graalvm.buildtools:native-maven-plugin:1.1.6:test (native-test) on project nitrite-native-tests: Execution native-test of goal org.graalvm.buildtools:native-maven-plugin:1.1.6:test failed: A required class was missing while executing org.graalvm.buildtools:native-maven-plugin:1.1.6:test: org/apache/maven/shared/utils/logging/MessageUtils
2026-07-27T16:44:59.5985609Z [ERROR] -----------------------------------------------------
2026-07-27T16:44:59.5986498Z [ERROR] realm =    extension>org.graalvm.buildtools:native-maven-plugin:1.1.6
2026-07-27T16:44:59.5988040Z [ERROR] strategy = org.codehaus.plexus.classworlds.strategy.SelfFirstStrategy
2026-07-27T16:44:59.5989745Z [ERROR] urls[0] = file:/home/runner/.m2/repository/org/graalvm/buildtools/native-maven-plugin/1.1.6/native-maven-plugin-1.1.6.jar
2026-07-27T16:44:59.5990968Z [ERROR] urls[1] = file:/home/runner/.m2/repository/org/graalvm/buildtools/utils/1.1.6/utils-1.1.6.jar
2026-07-27T16:44:59.5991918Z [ERROR] urls[2] = file:/home/runner/.m2/repository/com/github/openjson/openjson/1.0.13/openjson-1.0.13.jar
2026-07-27T16:44:59.6002065Z [ERROR] urls[3] = file:/home/runner/.m2/repository/org/graalvm/buildtools/graalvm-reachability-metadata/1.1.6/graalvm-reachability-metadata-1.1.6.jar
2026-07-27T16:44:59.6003259Z [ERROR] urls[4] = file:/home/runner/.m2/repository/org/cyclonedx/cyclonedx-maven-plugin/2.9.1/cyclonedx-maven-plugin-2.9.1.jar
2026-07-27T16:44:59.6004108Z [ERROR] urls[5] = file:/home/runner/.m2/repository/org/cyclonedx/cyclonedx-core-java/9.0.5/cyclonedx-core-java-9.0.5.jar
2026-07-27T16:44:59.6004799Z [ERROR] urls[6] = file:/home/runner/.m2/repository/commons-io/commons-io/2.16.1/commons-io-2.16.1.jar
2026-07-27T16:44:59.6005504Z [ERROR] urls[7] = file:/home/runner/.m2/repository/org/apache/commons/commons-collections4/4.4/commons-collections4-4.4.jar
2026-07-27T16:44:59.6006269Z [ERROR] urls[8] = file:/home/runner/.m2/repository/com/github/package-url/packageurl-java/1.5.0/packageurl-java-1.5.0.jar
2026-07-27T16:44:59.6007144Z [ERROR] urls[9] = file:/home/runner/.m2/repository/com/fasterxml/jackson/dataformat/jackson-dataformat-xml/2.17.2/jackson-dataformat-xml-2.17.2.jar
2026-07-27T16:44:59.6007982Z [ERROR] urls[10] = file:/home/runner/.m2/repository/com/fasterxml/jackson/core/jackson-core/2.17.2/jackson-core-2.17.2.jar
2026-07-27T16:44:59.6009021Z [ERROR] urls[11] = file:/home/runner/.m2/repository/com/fasterxml/jackson/core/jackson-annotations/2.17.2/jackson-annotations-2.17.2.jar
2026-07-27T16:44:59.6009839Z [ERROR] urls[12] = file:/home/runner/.m2/repository/com/fasterxml/jackson/core/jackson-databind/2.17.2/jackson-databind-2.17.2.jar
2026-07-27T16:44:59.6010563Z [ERROR] urls[13] = file:/home/runner/.m2/repository/org/codehaus/woodstox/stax2-api/4.2.2/stax2-api-4.2.2.jar
2026-07-27T16:44:59.6011478Z [ERROR] urls[14] = file:/home/runner/.m2/repository/com/fasterxml/woodstox/woodstox-core/6.7.0/woodstox-core-6.7.0.jar
2026-07-27T16:44:59.6012240Z [ERROR] urls[15] = file:/home/runner/.m2/repository/com/networknt/json-schema-validator/1.5.1/json-schema-validator-1.5.1.jar
2026-07-27T16:44:59.6012947Z [ERROR] urls[16] = file:/home/runner/.m2/repository/com/ethlo/time/itu/1.10.2/itu-1.10.2.jar
2026-07-27T16:44:59.6013701Z [ERROR] urls[17] = file:/home/runner/.m2/repository/com/fasterxml/jackson/dataformat/jackson-dataformat-yaml/2.17.1/jackson-dataformat-yaml-2.17.1.jar
2026-07-27T16:44:59.6014436Z [ERROR] urls[18] = file:/home/runner/.m2/repository/org/yaml/snakeyaml/2.2/snakeyaml-2.2.jar
2026-07-27T16:44:59.6015031Z [ERROR] urls[19] = file:/home/runner/.m2/repository/commons-codec/commons-codec/1.17.1/commons-codec-1.17.1.jar
2026-07-27T16:44:59.6015715Z [ERROR] urls[20] = file:/home/runner/.m2/repository/org/apache/commons/commons-lang3/3.17.0/commons-lang3-3.17.0.jar
2026-07-27T16:44:59.6016502Z [ERROR] urls[21] = file:/home/runner/.m2/repository/org/apache/maven/shared/maven-dependency-tree/3.3.0/maven-dependency-tree-3.3.0.jar
2026-07-27T16:44:59.6017374Z [ERROR] urls[22] = file:/home/runner/.m2/repository/org/apache/maven/shared/maven-dependency-analyzer/1.14.1/maven-dependency-analyzer-1.14.1.jar
2026-07-27T16:44:59.6018070Z [ERROR] urls[23] = file:/home/runner/.m2/repository/org/ow2/asm/asm/9.7/asm-9.7.jar
2026-07-27T16:44:59.6018865Z [ERROR] urls[24] = file:/home/runner/.m2/repository/org/twdata/maven/mojo-executor/2.4.1/mojo-executor-2.4.1.jar
2026-07-27T16:44:59.6019531Z [ERROR] urls[25] = file:/home/runner/.m2/repository/org/codehaus/plexus/plexus-utils/3.0.24/plexus-utils-3.0.24.jar
2026-07-27T16:44:59.6020021Z [ERROR] Number of foreign imports: 1
2026-07-27T16:44:59.6020420Z [ERROR] import: Entry[import  from realm ClassRealm[maven.api, parent: null]]
2026-07-27T16:44:59.6020965Z [ERROR] 
2026-07-27T16:44:59.6021352Z [ERROR] -----------------------------------------------------: org.apache.maven.shared.utils.logging.MessageUtils
2026-07-27T16:44:59.6021789Z [ERROR] -> [Help 1]
2026-07-27T16:44:59.6021991Z [ERROR] 
2026-07-27T16:44:59.6022296Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-07-27T16:44:59.6022752Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-07-27T16:44:59.6023082Z [ERROR] 
2026-07-27T16:44:59.6023467Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-07-27T16:44:59.6024102Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/PluginContainerException
2026-07-27T16:44:59.6184690Z ##[error]Process completed with exit code 1.
2026-07-27T16:44:59.6326175Z Post job cleanup.
2026-07-27T16:44:59.7220698Z [command]/usr/bin/git version
2026-07-27T16:44:59.7262538Z git version 2.54.0
2026-07-27T16:44:59.7299591Z Temporarily overriding HOME='/home/runner/work/_temp/60024bad-f9c7-45eb-9311-d881e04b89c1' before making global git config changes
2026-07-27T16:44:59.7300846Z Adding repository directory to the temporary git global config as a safe directory
2026-07-27T16:44:59.7305063Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/nitrite-java/nitrite-java
2026-07-27T16:44:59.7338997Z Removing SSH command configuration
2026-07-27T16:44:59.7345676Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-07-27T16:44:59.7383928Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-07-27T16:44:59.7643656Z Removing HTTP extra header
2026-07-27T16:44:59.7650892Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-27T16:44:59.7689153Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-07-27T16:44:59.7968759Z Removing includeIf entries pointing to credentials config files
2026-07-27T16:44:59.7975623Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-27T16:44:59.8009631Z includeif.gitdir:/home/runner/work/nitrite-java/nitrite-java/.git.path
2026-07-27T16:44:59.8010874Z includeif.gitdir:/home/runner/work/nitrite-java/nitrite-java/.git/worktrees/*.path
2026-07-27T16:44:59.8011984Z includeif.gitdir:/github/workspace/.git.path
2026-07-27T16:44:59.8012894Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-27T16:44:59.8020958Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/nitrite-java/nitrite-java/.git.path
2026-07-27T16:44:59.8049449Z /home/runner/work/_temp/git-credentials-2f998727-a731-4168-9959-f8d1d7cdfc18.config
2026-07-27T16:44:59.8059745Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/nitrite-java/nitrite-java/.git.path \/home\/runner\/work\/_temp\/git\-credentials\-2f998727\-a731\-4168\-9959\-f8d1d7cdfc18\.config
2026-07-27T16:44:59.8113118Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/nitrite-java/nitrite-java/.git/worktrees/*.path
2026-07-27T16:44:59.8142547Z /home/runner/work/_temp/git-credentials-2f998727-a731-4168-9959-f8d1d7cdfc18.config
2026-07-27T16:44:59.8151721Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/nitrite-java/nitrite-java/.git/worktrees/*.path \/home\/runner\/work\/_temp\/git\-credentials\-2f998727\-a731\-4168\-9959\-f8d1d7cdfc18\.config
2026-07-27T16:44:59.8194889Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-07-27T16:44:59.8232786Z /github/runner_temp/git-credentials-2f998727-a731-4168-9959-f8d1d7cdfc18.config
2026-07-27T16:44:59.8242865Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git.path \/github\/runner_temp\/git\-credentials\-2f998727\-a731\-4168\-9959\-f8d1d7cdfc18\.config
2026-07-27T16:44:59.8290144Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-27T16:44:59.8316413Z /github/runner_temp/git-credentials-2f998727-a731-4168-9959-f8d1d7cdfc18.config
2026-07-27T16:44:59.8325903Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path \/github\/runner_temp\/git\-credentials\-2f998727\-a731\-4168\-9959\-f8d1d7cdfc18\.config
2026-07-27T16:44:59.8371353Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-07-27T16:44:59.8633397Z Removing credentials config '/home/runner/work/_temp/git-credentials-2f998727-a731-4168-9959-f8d1d7cdfc18.config'
2026-07-27T16:44:59.8792524Z Cleaning up orphan processes
2026-07-27T16:44:59.9107940Z Terminate orphan process: pid (2780) (java)
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 31. `openremote__openremote__086149354006.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/openremote__openremote__086149354006.txt` (authoritative; read this, not the excerpt)
- **Repository**: `openremote/openremote`
- **Content hash (sha256, first 16)**: `0611218da9353e8a`
- **Body size**: 212,849 bytes, 1,872 lines
- **Excerpt**: final 120 of 1,872 lines, content-blind

```text
2026-07-09T15:08:39.4045746Z 
2026-07-09T15:08:39.4064172Z > Task :test:test FAILED
2026-07-09T15:08:39.5073939Z 
2026-07-09T15:08:39.5073972Z 
2026-07-09T15:08:39.5097586Z [Incubating] Problems report is available at: file:///home/runner/work/openremote/openremote/build/reports/problems/problems-report.html
2026-07-09T15:08:39.5103468Z FAILURE: Build failed with an exception.
2026-07-09T15:08:39.5103856Z 
2026-07-09T15:08:39.5104279Z Deprecated Gradle features were used in this build, making it incompatible with Gradle 10.
2026-07-09T15:08:39.5104856Z 
2026-07-09T15:08:39.5105525Z You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.
2026-07-09T15:08:39.5106304Z 
2026-07-09T15:08:39.5107062Z For more on this, please refer to https://docs.gradle.org/9.6.1/userguide/command_line_interface.html#sec:command_line_warnings in the Gradle documentation.
2026-07-09T15:08:39.5108201Z 27 actionable tasks: 27 executed
2026-07-09T15:08:39.5119393Z 
2026-07-09T15:08:39.5120093Z * What went wrong:
2026-07-09T15:08:39.5120789Z Execution failed for task ':test:test'.
2026-07-09T15:08:39.5122137Z > There were failing tests. See the report at: file:///home/runner/work/openremote/openremote/test/build/reports/tests/test/index.html
2026-07-09T15:08:39.5123281Z 
2026-07-09T15:08:39.5123424Z * Try:
2026-07-09T15:08:39.5124011Z > Run with --scan to get full insights from a Build Scan (powered by Develocity).
2026-07-09T15:08:39.5124527Z 
2026-07-09T15:08:39.5124689Z BUILD FAILED in 17m 20s
2026-07-09T15:08:39.6045387Z Configuration cache entry stored.
2026-07-09T15:08:40.0753809Z ##[error]Process completed with exit code 1.
2026-07-09T15:08:40.0849223Z ##[group]Run actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a
2026-07-09T15:08:40.0849650Z with:
2026-07-09T15:08:40.0849883Z   name: or-integration-test-results
2026-07-09T15:08:40.0850168Z   path: test/build/reports/tests
2026-07-09T15:08:40.0850435Z   if-no-files-found: warn
2026-07-09T15:08:40.0850676Z   compression-level: 6
2026-07-09T15:08:40.0850897Z   overwrite: false
2026-07-09T15:08:40.0851114Z   include-hidden-files: false
2026-07-09T15:08:40.0851360Z   archive: true
2026-07-09T15:08:40.0851566Z env:
2026-07-09T15:08:40.0851880Z   JAVA_HOME: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/21.0.11-10/x64
2026-07-09T15:08:40.0852381Z   JAVA_HOME_21_X64: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/21.0.11-10/x64
2026-07-09T15:08:40.0853198Z   MAVEN_ARGS: -ntp
2026-07-09T15:08:40.0853473Z ##[endgroup]
2026-07-09T15:08:40.3094102Z With the provided path, there will be 379 files uploaded
2026-07-09T15:08:40.3095757Z Artifact name is valid!
2026-07-09T15:08:40.3096429Z Root directory input is valid!
2026-07-09T15:08:40.5940523Z Uploading artifact: or-integration-test-results.zip
2026-07-09T15:08:40.5979320Z Beginning upload of artifact content to blob storage
2026-07-09T15:08:42.5512964Z Uploaded bytes 6364583
2026-07-09T15:08:42.6071684Z Finished uploading artifact content to blob storage!
2026-07-09T15:08:42.6075980Z SHA256 digest of uploaded artifact is b64c1ab5c64b12efe4cfae6d35d51fceb662d1fedc3e1af26f0de8012eab3f98
2026-07-09T15:08:42.6078194Z Finalizing artifact upload
2026-07-09T15:08:42.9454263Z Artifact or-integration-test-results successfully finalized. Artifact ID 8202575483
2026-07-09T15:08:42.9455633Z Artifact or-integration-test-results has been successfully uploaded! Final size is 6364583 bytes. Artifact ID is 8202575483
2026-07-09T15:08:42.9474139Z Artifact download URL: https://github.com/openremote/openremote/actions/runs/29026970986/artifacts/8202575483
2026-07-09T15:08:42.9694897Z ##[group]Run actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a
2026-07-09T15:08:42.9695579Z with:
2026-07-09T15:08:42.9695914Z   name: or-integration-test-outputs
2026-07-09T15:08:42.9697088Z   path: test/build/classes/java/main/**
test/build/classes/java/test/**
test/build/jacoco/*.exec
test/build/reports/tests/test/**
test/build/test-results/test/**

2026-07-09T15:08:42.9698304Z   if-no-files-found: warn
2026-07-09T15:08:42.9698690Z   compression-level: 6
2026-07-09T15:08:42.9699047Z   overwrite: false
2026-07-09T15:08:42.9699399Z   include-hidden-files: false
2026-07-09T15:08:42.9699801Z   archive: true
2026-07-09T15:08:42.9700112Z env:
2026-07-09T15:08:42.9700599Z   JAVA_HOME: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/21.0.11-10/x64
2026-07-09T15:08:42.9701462Z   JAVA_HOME_21_X64: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/21.0.11-10/x64
2026-07-09T15:08:42.9702119Z   MAVEN_ARGS: -ntp
2026-07-09T15:08:42.9702448Z ##[endgroup]
2026-07-09T15:08:43.2646276Z Multiple search paths detected. Calculating the least common ancestor of all paths
2026-07-09T15:08:43.2649118Z The least common ancestor is /home/runner/work/openremote/openremote/test/build. This will be the root directory of the artifact
2026-07-09T15:08:43.2650243Z With the provided path, there will be 468 files uploaded
2026-07-09T15:08:43.2651067Z Artifact name is valid!
2026-07-09T15:08:43.2651486Z Root directory input is valid!
2026-07-09T15:08:43.5551807Z Uploading artifact: or-integration-test-outputs.zip
2026-07-09T15:08:43.5592089Z Beginning upload of artifact content to blob storage
2026-07-09T15:08:45.9683510Z Uploaded bytes 8388608
2026-07-09T15:08:46.7554115Z Uploaded bytes 16777216
2026-07-09T15:08:47.1899720Z Uploaded bytes 20025378
2026-07-09T15:08:47.2465770Z Finished uploading artifact content to blob storage!
2026-07-09T15:08:47.2469337Z SHA256 digest of uploaded artifact is 54447d6fa074eed26748d3df026e22d38bd0e5810e3da31bd3a28ba03a3abdd0
2026-07-09T15:08:47.2471785Z Finalizing artifact upload
2026-07-09T15:08:47.6001081Z Artifact or-integration-test-outputs successfully finalized. Artifact ID 8202577905
2026-07-09T15:08:47.6002106Z Artifact or-integration-test-outputs has been successfully uploaded! Final size is 20025378 bytes. Artifact ID is 8202577905
2026-07-09T15:08:47.6007211Z Artifact download URL: https://github.com/openremote/openremote/actions/runs/29026970986/artifacts/8202577905
2026-07-09T15:08:47.6276682Z Post job cleanup.
2026-07-09T15:08:47.7713554Z Post job cleanup.
2026-07-09T15:08:47.8567460Z [command]/usr/bin/git version
2026-07-09T15:08:47.8638301Z git version 2.54.0
2026-07-09T15:08:47.8680585Z Temporarily overriding HOME='/home/runner/work/_temp/32fdd287-2609-427f-8729-4e46b12a1915' before making global git config changes
2026-07-09T15:08:47.8682456Z Adding repository directory to the temporary git global config as a safe directory
2026-07-09T15:08:47.8686756Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/openremote/openremote
2026-07-09T15:08:47.8743471Z Removing SSH command configuration
2026-07-09T15:08:47.8744168Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-07-09T15:08:47.8761867Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-07-09T15:08:47.9008114Z Removing HTTP extra header
2026-07-09T15:08:47.9008909Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-09T15:08:47.9044321Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-07-09T15:08:47.9290738Z Removing includeIf entries pointing to credentials config files
2026-07-09T15:08:47.9298209Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-09T15:08:47.9328599Z includeif.gitdir:/home/runner/work/openremote/openremote/.git.path
2026-07-09T15:08:47.9330025Z includeif.gitdir:/home/runner/work/openremote/openremote/.git/worktrees/*.path
2026-07-09T15:08:47.9330835Z includeif.gitdir:/github/workspace/.git.path
2026-07-09T15:08:47.9331449Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-09T15:08:47.9337770Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/openremote/openremote/.git.path
2026-07-09T15:08:47.9362212Z /home/runner/work/_temp/git-credentials-ff34dd3b-93ba-4ac4-87a2-1c8c07204f0f.config
2026-07-09T15:08:47.9373951Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/openremote/openremote/.git.path /home/runner/work/_temp/git-credentials-ff34dd3b-93ba-4ac4-87a2-1c8c07204f0f.config
2026-07-09T15:08:47.9444545Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/openremote/openremote/.git/worktrees/*.path
2026-07-09T15:08:47.9446075Z /home/runner/work/_temp/git-credentials-ff34dd3b-93ba-4ac4-87a2-1c8c07204f0f.config
2026-07-09T15:08:47.9451632Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/openremote/openremote/.git/worktrees/*.path /home/runner/work/_temp/git-credentials-ff34dd3b-93ba-4ac4-87a2-1c8c07204f0f.config
2026-07-09T15:08:47.9492214Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-07-09T15:08:47.9518477Z /github/runner_temp/git-credentials-ff34dd3b-93ba-4ac4-87a2-1c8c07204f0f.config
2026-07-09T15:08:47.9529364Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git.path /github/runner_temp/git-credentials-ff34dd3b-93ba-4ac4-87a2-1c8c07204f0f.config
2026-07-09T15:08:47.9564782Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-09T15:08:47.9589493Z /github/runner_temp/git-credentials-ff34dd3b-93ba-4ac4-87a2-1c8c07204f0f.config
2026-07-09T15:08:47.9598229Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path /github/runner_temp/git-credentials-ff34dd3b-93ba-4ac4-87a2-1c8c07204f0f.config
2026-07-09T15:08:47.9636422Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-07-09T15:08:47.9891639Z Removing credentials config '/home/runner/work/_temp/git-credentials-ff34dd3b-93ba-4ac4-87a2-1c8c07204f0f.config'
2026-07-09T15:08:48.0069740Z Cleaning up orphan processes
2026-07-09T15:08:48.0532579Z Terminate orphan process: pid (3232) (java)
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 32. `openremote__openremote__086930896418.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/openremote__openremote__086930896418.txt` (authoritative; read this, not the excerpt)
- **Repository**: `openremote/openremote`
- **Content hash (sha256, first 16)**: `5abd32671222f73a`
- **Body size**: 186,288 bytes, 1,753 lines
- **Excerpt**: final 120 of 1,753 lines, content-blind

```text
2026-07-13T21:03:56.2314181Z 
2026-07-13T21:03:56.2314911Z > Task :test:test FAILED
2026-07-13T21:03:56.2315133Z 
2026-07-13T21:03:56.2315810Z [Incubating] Problems report is available at: file:///home/runner/work/openremote/openremote/build/reports/problems/problems-report.html
2026-07-13T21:03:56.3312664Z 
2026-07-13T21:03:56.3315733Z FAILURE: Build failed with an exception.
2026-07-13T21:03:56.3316216Z 
2026-07-13T21:03:56.3316361Z 
2026-07-13T21:03:56.3316812Z Deprecated Gradle features were used in this build, making it incompatible with Gradle 10.
2026-07-13T21:03:56.3317511Z * What went wrong:
2026-07-13T21:03:56.3317749Z 
2026-07-13T21:03:56.3318015Z Execution failed for task ':test:test'.
2026-07-13T21:03:56.3318877Z You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.
2026-07-13T21:03:56.3320340Z > There were failing tests. See the report at: file:///home/runner/work/openremote/openremote/test/build/reports/tests/test/index.html
2026-07-13T21:03:56.3321050Z 
2026-07-13T21:03:56.3321186Z 
2026-07-13T21:03:56.3321859Z For more on this, please refer to https://docs.gradle.org/9.6.1/userguide/command_line_interface.html#sec:command_line_warnings in the Gradle documentation.
2026-07-13T21:03:56.3322820Z * Try:
2026-07-13T21:03:56.3323165Z 27 actionable tasks: 27 executed
2026-07-13T21:03:56.3323751Z > Run with --scan to get full insights from a Build Scan (powered by Develocity).
2026-07-13T21:03:56.3324341Z Configuration cache entry stored.
2026-07-13T21:03:56.3324676Z 
2026-07-13T21:03:56.3324988Z BUILD FAILED in 17m 8s
2026-07-13T21:03:56.7813582Z ##[error]Process completed with exit code 1.
2026-07-13T21:03:56.7876039Z ##[group]Run actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a
2026-07-13T21:03:56.7876362Z with:
2026-07-13T21:03:56.7876533Z   name: or-integration-test-results
2026-07-13T21:03:56.7876749Z   path: test/build/reports/tests
2026-07-13T21:03:56.7876944Z   if-no-files-found: warn
2026-07-13T21:03:56.7877126Z   compression-level: 6
2026-07-13T21:03:56.7877294Z   overwrite: false
2026-07-13T21:03:56.7877458Z   include-hidden-files: false
2026-07-13T21:03:56.7877641Z   archive: true
2026-07-13T21:03:56.7877789Z env:
2026-07-13T21:03:56.7878020Z   JAVA_HOME: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/21.0.11-10/x64
2026-07-13T21:03:56.7878409Z   JAVA_HOME_21_X64: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/21.0.11-10/x64
2026-07-13T21:03:56.7878705Z   MAVEN_ARGS: -ntp
2026-07-13T21:03:56.7878871Z ##[endgroup]
2026-07-13T21:03:56.9542515Z With the provided path, there will be 382 files uploaded
2026-07-13T21:03:56.9546236Z Artifact name is valid!
2026-07-13T21:03:56.9546794Z Root directory input is valid!
2026-07-13T21:03:57.2365231Z Uploading artifact: or-integration-test-results.zip
2026-07-13T21:03:57.2414878Z Beginning upload of artifact content to blob storage
2026-07-13T21:03:58.8486325Z Uploaded bytes 6136669
2026-07-13T21:03:58.9104177Z Finished uploading artifact content to blob storage!
2026-07-13T21:03:58.9106576Z SHA256 digest of uploaded artifact is 33ab262add39716728e1e15021dfa267e420242bc70a40b16fe9384ef43b7f8f
2026-07-13T21:03:58.9108630Z Finalizing artifact upload
2026-07-13T21:03:59.2405135Z Artifact or-integration-test-results successfully finalized. Artifact ID 8292751179
2026-07-13T21:03:59.2406107Z Artifact or-integration-test-results has been successfully uploaded! Final size is 6136669 bytes. Artifact ID is 8292751179
2026-07-13T21:03:59.2410516Z Artifact download URL: https://github.com/openremote/openremote/actions/runs/29283674131/artifacts/8292751179
2026-07-13T21:03:59.2553921Z ##[group]Run actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a
2026-07-13T21:03:59.2554236Z with:
2026-07-13T21:03:59.2554415Z   name: or-integration-test-outputs
2026-07-13T21:03:59.2554920Z   path: test/build/classes/java/main/**
test/build/classes/java/test/**
test/build/jacoco/*.exec
test/build/reports/tests/test/**
test/build/test-results/test/**

2026-07-13T21:03:59.2555418Z   if-no-files-found: warn
2026-07-13T21:03:59.2555610Z   compression-level: 6
2026-07-13T21:03:59.2555784Z   overwrite: false
2026-07-13T21:03:59.2555958Z   include-hidden-files: false
2026-07-13T21:03:59.2556153Z   archive: true
2026-07-13T21:03:59.2556307Z env:
2026-07-13T21:03:59.2556547Z   JAVA_HOME: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/21.0.11-10/x64
2026-07-13T21:03:59.2557081Z   JAVA_HOME_21_X64: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/21.0.11-10/x64
2026-07-13T21:03:59.2557384Z   MAVEN_ARGS: -ntp
2026-07-13T21:03:59.2557556Z ##[endgroup]
2026-07-13T21:03:59.4401163Z Multiple search paths detected. Calculating the least common ancestor of all paths
2026-07-13T21:03:59.4403464Z The least common ancestor is /home/runner/work/openremote/openremote/test/build. This will be the root directory of the artifact
2026-07-13T21:03:59.4404331Z With the provided path, there will be 471 files uploaded
2026-07-13T21:03:59.4407833Z Artifact name is valid!
2026-07-13T21:03:59.4408220Z Root directory input is valid!
2026-07-13T21:03:59.7195426Z Uploading artifact: or-integration-test-outputs.zip
2026-07-13T21:03:59.7225234Z Beginning upload of artifact content to blob storage
2026-07-13T21:04:01.6003871Z Uploaded bytes 8388608
2026-07-13T21:04:02.0953635Z Uploaded bytes 16777216
2026-07-13T21:04:02.2485089Z Uploaded bytes 19239244
2026-07-13T21:04:02.3109929Z Finished uploading artifact content to blob storage!
2026-07-13T21:04:02.3112415Z SHA256 digest of uploaded artifact is 785a59e6fe3aa6af95080eed0dbb5182804f6141d924bb3353964cd1e84cf73a
2026-07-13T21:04:02.3114475Z Finalizing artifact upload
2026-07-13T21:04:02.6703063Z Artifact or-integration-test-outputs successfully finalized. Artifact ID 8292752509
2026-07-13T21:04:02.6704012Z Artifact or-integration-test-outputs has been successfully uploaded! Final size is 19239244 bytes. Artifact ID is 8292752509
2026-07-13T21:04:02.6708301Z Artifact download URL: https://github.com/openremote/openremote/actions/runs/29283674131/artifacts/8292752509
2026-07-13T21:04:02.6903035Z Post job cleanup.
2026-07-13T21:04:02.8039569Z Post job cleanup.
2026-07-13T21:04:02.8683294Z [command]/usr/bin/git version
2026-07-13T21:04:02.8713814Z git version 2.54.0
2026-07-13T21:04:02.8740396Z Temporarily overriding HOME='/home/runner/work/_temp/2c91544d-ca24-42ad-9e2d-15570fa7bd79' before making global git config changes
2026-07-13T21:04:02.8741379Z Adding repository directory to the temporary git global config as a safe directory
2026-07-13T21:04:02.8749833Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/openremote/openremote
2026-07-13T21:04:02.8774096Z Removing SSH command configuration
2026-07-13T21:04:02.8778615Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-07-13T21:04:02.8804609Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-07-13T21:04:02.9010651Z Removing HTTP extra header
2026-07-13T21:04:02.9015096Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-13T21:04:02.9045444Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-07-13T21:04:02.9243067Z Removing includeIf entries pointing to credentials config files
2026-07-13T21:04:02.9249962Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-13T21:04:02.9302731Z includeif.gitdir:/home/runner/work/openremote/openremote/.git.path
2026-07-13T21:04:02.9303455Z includeif.gitdir:/home/runner/work/openremote/openremote/.git/worktrees/*.path
2026-07-13T21:04:02.9304238Z includeif.gitdir:/github/workspace/.git.path
2026-07-13T21:04:02.9304786Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-13T21:04:02.9311118Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/openremote/openremote/.git.path
2026-07-13T21:04:02.9331315Z /home/runner/work/_temp/git-credentials-61efb5d6-451e-4dfb-8841-d89b59864e92.config
2026-07-13T21:04:02.9340828Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/openremote/openremote/.git.path /home/runner/work/_temp/git-credentials-61efb5d6-451e-4dfb-8841-d89b59864e92.config
2026-07-13T21:04:02.9372056Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/openremote/openremote/.git/worktrees/*.path
2026-07-13T21:04:02.9391964Z /home/runner/work/_temp/git-credentials-61efb5d6-451e-4dfb-8841-d89b59864e92.config
2026-07-13T21:04:02.9400186Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/openremote/openremote/.git/worktrees/*.path /home/runner/work/_temp/git-credentials-61efb5d6-451e-4dfb-8841-d89b59864e92.config
2026-07-13T21:04:02.9450429Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-07-13T21:04:02.9471079Z /github/runner_temp/git-credentials-61efb5d6-451e-4dfb-8841-d89b59864e92.config
2026-07-13T21:04:02.9480004Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git.path /github/runner_temp/git-credentials-61efb5d6-451e-4dfb-8841-d89b59864e92.config
2026-07-13T21:04:02.9509868Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-13T21:04:02.9522438Z /github/runner_temp/git-credentials-61efb5d6-451e-4dfb-8841-d89b59864e92.config
2026-07-13T21:04:02.9529854Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path /github/runner_temp/git-credentials-61efb5d6-451e-4dfb-8841-d89b59864e92.config
2026-07-13T21:04:02.9560656Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-07-13T21:04:02.9753337Z Removing credentials config '/home/runner/work/_temp/git-credentials-61efb5d6-451e-4dfb-8841-d89b59864e92.config'
2026-07-13T21:04:02.9871941Z Cleaning up orphan processes
2026-07-13T21:04:03.0229601Z Terminate orphan process: pid (3012) (java)
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 33. `sirixdb__sirix__088196470656.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/sirixdb__sirix__088196470656.txt` (authoritative; read this, not the excerpt)
- **Repository**: `sirixdb/sirix`
- **Content hash (sha256, first 16)**: `d4932af43685ad17`
- **Body size**: 3,059,931 bytes, 19,576 lines
- **Excerpt**: final 120 of 19,576 lines, content-blind

```text
2026-07-19T13:49:41.7777610Z 	at org.gradle.internal.execution.steps.legacy.MarkSnapshottingInputsFinishedStep.execute(MarkSnapshottingInputsFinishedStep.java:27)
2026-07-19T13:49:41.7778860Z 	at org.gradle.internal.execution.steps.ResolveMutableCachingStateStep.executeDelegate(ResolveMutableCachingStateStep.java:70)
2026-07-19T13:49:41.7779980Z 	at org.gradle.internal.execution.steps.ResolveMutableCachingStateStep.executeDelegate(ResolveMutableCachingStateStep.java:32)
2026-07-19T13:49:41.7781310Z 	at org.gradle.internal.execution.steps.AbstractResolveCachingStateStep.execute(AbstractResolveCachingStateStep.java:69)
2026-07-19T13:49:41.7782400Z 	at org.gradle.internal.execution.steps.AbstractResolveCachingStateStep.execute(AbstractResolveCachingStateStep.java:37)
2026-07-19T13:49:41.7783470Z 	at org.gradle.internal.execution.steps.ResolveChangesStep.executeMutable(ResolveChangesStep.java:63)
2026-07-19T13:49:41.7784600Z 	at org.gradle.internal.execution.steps.ResolveChangesStep.executeMutable(ResolveChangesStep.java:34)
2026-07-19T13:49:41.7785510Z 	at org.gradle.internal.execution.steps.MutableStep.execute(MutableStep.java:26)
2026-07-19T13:49:41.7786700Z 	at org.gradle.internal.execution.steps.ValidateStep$Mutable.executeDelegate(ValidateStep.java:79)
2026-07-19T13:49:41.7787620Z 	at org.gradle.internal.execution.steps.ValidateStep$Mutable.executeDelegate(ValidateStep.java:65)
2026-07-19T13:49:41.7789190Z 	at org.gradle.internal.execution.steps.ValidateStep.execute(ValidateStep.java:99)
2026-07-19T13:49:41.7791320Z 	at org.gradle.internal.execution.steps.ValidateStep$Mutable.execute(ValidateStep.java:65)
2026-07-19T13:49:41.7794610Z 	at org.gradle.internal.execution.steps.CaptureMutableStateBeforeExecutionStep.executeMutable(CaptureMutableStateBeforeExecutionStep.java:86)
2026-07-19T13:49:41.7797740Z 	at org.gradle.internal.execution.steps.CaptureMutableStateBeforeExecutionStep.execute(CaptureMutableStateBeforeExecutionStep.java:65)
2026-07-19T13:49:41.7800340Z 	at org.gradle.internal.execution.steps.CaptureMutableStateBeforeExecutionStep.execute(CaptureMutableStateBeforeExecutionStep.java:45)
2026-07-19T13:49:41.7802960Z 	at org.gradle.internal.execution.steps.SkipEmptyMutableWorkStep.executeWithNonEmptySources(SkipEmptyMutableWorkStep.java:210)
2026-07-19T13:49:41.7805270Z 	at org.gradle.internal.execution.steps.SkipEmptyMutableWorkStep.executeMutable(SkipEmptyMutableWorkStep.java:90)
2026-07-19T13:49:41.7808100Z 	at org.gradle.internal.execution.steps.SkipEmptyMutableWorkStep.executeMutable(SkipEmptyMutableWorkStep.java:53)
2026-07-19T13:49:41.7809520Z 	at org.gradle.internal.execution.steps.MutableStep.execute(MutableStep.java:26)
2026-07-19T13:49:41.7811430Z 	at org.gradle.internal.execution.steps.legacy.MarkSnapshottingInputsStartedStep.execute(MarkSnapshottingInputsStartedStep.java:38)
2026-07-19T13:49:41.7812830Z 	at org.gradle.internal.execution.steps.LoadPreviousExecutionStateStep.executeMutable(LoadPreviousExecutionStateStep.java:36)
2026-07-19T13:49:41.7813830Z 	at org.gradle.internal.execution.steps.LoadPreviousExecutionStateStep.executeMutable(LoadPreviousExecutionStateStep.java:23)
2026-07-19T13:49:41.7814630Z 	at org.gradle.internal.execution.steps.MutableStep.execute(MutableStep.java:26)
2026-07-19T13:49:41.7815290Z 	at org.gradle.internal.execution.steps.HandleStaleOutputsStep.executeMutable(HandleStaleOutputsStep.java:77)
2026-07-19T13:49:41.7816140Z 	at org.gradle.internal.execution.steps.HandleStaleOutputsStep.executeMutable(HandleStaleOutputsStep.java:43)
2026-07-19T13:49:41.7816850Z 	at org.gradle.internal.execution.steps.MutableStep.execute(MutableStep.java:26)
2026-07-19T13:49:41.7817840Z 	at org.gradle.internal.execution.steps.AssignMutableWorkspaceStep.lambda$executeMutable$0(AssignMutableWorkspaceStep.java:34)
2026-07-19T13:49:41.7818750Z 	at org.gradle.api.internal.tasks.execution.TaskExecution$4.withWorkspace(TaskExecution.java:305)
2026-07-19T13:49:41.7820040Z 	at org.gradle.internal.execution.steps.AssignMutableWorkspaceStep.executeMutable(AssignMutableWorkspaceStep.java:30)
2026-07-19T13:49:41.7820890Z 	at org.gradle.internal.execution.steps.AssignMutableWorkspaceStep.executeMutable(AssignMutableWorkspaceStep.java:21)
2026-07-19T13:49:41.7821550Z 	at org.gradle.internal.execution.steps.MutableStep.execute(MutableStep.java:26)
2026-07-19T13:49:41.7823150Z 	at org.gradle.internal.execution.steps.ChoosePipelineStep.execute(ChoosePipelineStep.java:40)
2026-07-19T13:49:41.7823800Z 	at org.gradle.internal.execution.steps.ChoosePipelineStep.execute(ChoosePipelineStep.java:23)
2026-07-19T13:49:41.7824570Z 	at org.gradle.internal.execution.steps.ExecuteWorkBuildOperationFiringStep.lambda$execute$2(ExecuteWorkBuildOperationFiringStep.java:67)
2026-07-19T13:49:41.7825460Z 	at org.gradle.internal.execution.steps.ExecuteWorkBuildOperationFiringStep.execute(ExecuteWorkBuildOperationFiringStep.java:67)
2026-07-19T13:49:41.7826570Z 	at org.gradle.internal.execution.steps.ExecuteWorkBuildOperationFiringStep.execute(ExecuteWorkBuildOperationFiringStep.java:39)
2026-07-19T13:49:41.7827450Z 	at org.gradle.internal.execution.steps.IdentityCacheStep.execute(IdentityCacheStep.java:46)
2026-07-19T13:49:41.7828050Z 	at org.gradle.internal.execution.steps.IdentityCacheStep.execute(IdentityCacheStep.java:34)
2026-07-19T13:49:41.7828600Z 	at org.gradle.internal.execution.steps.IdentifyStep.execute(IdentifyStep.java:56)
2026-07-19T13:49:41.7829150Z 	at org.gradle.internal.execution.steps.IdentifyStep.execute(IdentifyStep.java:38)
2026-07-19T13:49:41.7831250Z 	at org.gradle.internal.execution.impl.DefaultExecutionEngine$1.execute(DefaultExecutionEngine.java:68)
2026-07-19T13:49:41.7832010Z 	at org.gradle.api.internal.tasks.execution.ExecuteActionsTaskExecuter.executeIfValid(ExecuteActionsTaskExecuter.java:132)
2026-07-19T13:49:41.7832540Z 	... 61 more
2026-07-19T13:49:41.7832650Z 
2026-07-19T13:49:41.7832650Z 
2026-07-19T13:49:41.7832720Z BUILD FAILED in 40m 21s
2026-07-19T13:49:41.7832860Z 
2026-07-19T13:49:41.7833090Z Deprecated Gradle features were used in this build, making it incompatible with Gradle 10.
2026-07-19T13:49:41.7833400Z 
2026-07-19T13:49:41.7833750Z You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.
2026-07-19T13:49:41.7834180Z 
2026-07-19T13:49:41.7834600Z For more on this, please refer to https://docs.gradle.org/9.4.1/userguide/command_line_interface.html#sec:command_line_warnings in the Gradle documentation.
2026-07-19T13:49:41.7835420Z 29 actionable tasks: 29 executed
2026-07-19T13:49:42.4388610Z ##[error]Process completed with exit code 1.
2026-07-19T13:49:42.4901330Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-07-19T13:49:42.4902720Z ##[group]Run actions/upload-artifact@v4
2026-07-19T13:49:42.4902960Z with:
2026-07-19T13:49:42.4903320Z   name: test-reports-macos-latest
2026-07-19T13:49:42.4903790Z   path: **/build/reports/tests/test
2026-07-19T13:49:42.4931800Z   retention-days: 14
2026-07-19T13:49:42.4932130Z   if-no-files-found: warn
2026-07-19T13:49:42.4932610Z   compression-level: 6
2026-07-19T13:49:42.4932940Z   overwrite: false
2026-07-19T13:49:42.4933460Z   include-hidden-files: false
2026-07-19T13:49:42.4933680Z env:
2026-07-19T13:49:42.4933870Z   GRADLE_OPTS: -Dorg.gradle.jvmargs=-Xmx4g
2026-07-19T13:49:42.4934360Z   JAVA_HOME: /Users/runner/hostedtoolcache/Java_Temurin-Hotspot_jdk/25.0.3-9.0/arm64/Contents/Home
2026-07-19T13:49:42.4935340Z   JAVA_HOME_25_ARM64: /Users/runner/hostedtoolcache/Java_Temurin-Hotspot_jdk/25.0.3-9.0/arm64/Contents/Home
2026-07-19T13:49:42.4935800Z   GRADLE_ACTION_ID: gradle/actions/setup-gradle
2026-07-19T13:49:42.4936060Z   GRADLE_USER_HOME: /Users/runner/.gradle
2026-07-19T13:49:42.4936310Z   GRADLE_BUILD_ACTION_SETUP_COMPLETED: true
2026-07-19T13:49:42.4936560Z   GRADLE_BUILD_ACTION_CACHE_RESTORED: true
2026-07-19T13:49:42.4936940Z   DEVELOCITY_INJECTION_INIT_SCRIPT_NAME: gradle-actions.inject-develocity.init.gradle
2026-07-19T13:49:42.4937360Z   DEVELOCITY_INJECTION_CUSTOM_VALUE: gradle-actions
2026-07-19T13:49:42.4937640Z   GITHUB_DEPENDENCY_GRAPH_ENABLED: false
2026-07-19T13:49:42.4937870Z ##[endgroup]
2026-07-19T13:49:43.2368780Z (node:49799) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-07-19T13:49:43.2371450Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-07-19T13:49:44.2250640Z With the provided path, there will be 3000 files uploaded
2026-07-19T13:49:44.2251060Z Artifact name is valid!
2026-07-19T13:49:44.2251250Z Root directory input is valid!
2026-07-19T13:49:44.5130440Z Beginning upload of artifact content to blob storage
2026-07-19T13:49:45.7648910Z (node:49799) [DEP0169] DeprecationWarning: `url.parse()` behavior is not standardized and prone to errors that have security implications. Use the WHATWG URL API instead. CVEs are not issued for `url.parse()` vulnerabilities.
2026-07-19T13:49:46.2003210Z Uploaded bytes 3886867
2026-07-19T13:49:46.2465440Z Finished uploading artifact content to blob storage!
2026-07-19T13:49:46.2474690Z SHA256 digest of uploaded artifact zip is 85e3e7c2580e107063c4c63610b0c6d75c59e0d70f75c8ff96ce3529c712a60a
2026-07-19T13:49:46.2477520Z Finalizing artifact upload
2026-07-19T13:49:46.4471630Z Artifact test-reports-macos-latest.zip successfully finalized. Artifact ID 8443156371
2026-07-19T13:49:46.4475400Z Artifact test-reports-macos-latest has been successfully uploaded! Final size is 3886867 bytes. Artifact ID is 8443156371
2026-07-19T13:49:46.4518830Z Artifact download URL: https://github.com/sirixdb/sirix/actions/runs/29688264737/artifacts/8443156371
2026-07-19T13:49:46.4877750Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-07-19T13:49:46.4878780Z Post job cleanup.
2026-07-19T13:49:46.7550290Z In post-action step
2026-07-19T13:49:46.7556850Z Cache is read-only: will not save state for use in subsequent builds.
2026-07-19T13:49:46.7570430Z Generating Job Summary
2026-07-19T13:49:46.7575040Z Completed post-action step
2026-07-19T13:49:46.7716290Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-07-19T13:49:46.7717470Z Post job cleanup.
2026-07-19T13:49:46.9485070Z (node:49817) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-07-19T13:49:46.9485760Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-07-19T13:49:46.9598080Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-07-19T13:49:46.9599290Z Post job cleanup.
2026-07-19T13:49:47.0956260Z [command]/opt/homebrew/bin/git version
2026-07-19T13:49:47.1298900Z git version 2.55.0
2026-07-19T13:49:47.1320950Z Copying '/Users/runner/.gitconfig' to '/Users/runner/work/_temp/6209f5e9-0f32-49f1-9378-80c48e881466/.gitconfig'
2026-07-19T13:49:47.1325130Z Temporarily overriding HOME='/Users/runner/work/_temp/6209f5e9-0f32-49f1-9378-80c48e881466' before making global git config changes
2026-07-19T13:49:47.1326080Z Adding repository directory to the temporary git global config as a safe directory
2026-07-19T13:49:47.1328720Z [command]/opt/homebrew/bin/git config --global --add safe.directory /Users/runner/work/sirix/sirix
2026-07-19T13:49:47.1471820Z [command]/opt/homebrew/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-07-19T13:49:47.1547130Z [command]/opt/homebrew/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-07-19T13:49:47.3112590Z [command]/opt/homebrew/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-19T13:49:47.3183520Z http.https://github.com/.extraheader
2026-07-19T13:49:47.3202100Z [command]/opt/homebrew/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-07-19T13:49:47.3298960Z [command]/opt/homebrew/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-07-19T13:49:47.4642090Z [command]/opt/homebrew/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-19T13:49:47.4820720Z [command]/opt/homebrew/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-07-19T13:49:47.6222920Z Cleaning up orphan processes
2026-07-19T13:49:48.3019390Z Terminate orphan process: pid (49325) (java)
2026-07-19T13:49:51.3889790Z Terminate orphan process: pid (2209) (java)
2026-07-19T13:49:51.4077970Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/checkout@v4, actions/setup-java@v4, actions/upload-artifact@v4, gradle/actions/setup-gradle@v4. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 34. `sirixdb__sirix__092355497985.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/sirixdb__sirix__092355497985.txt` (authoritative; read this, not the excerpt)
- **Repository**: `sirixdb/sirix`
- **Content hash (sha256, first 16)**: `4a40b85a5c74b1aa`
- **Body size**: 340,158 bytes, 3,943 lines
- **Excerpt**: final 120 of 3,943 lines, content-blind

```text
2026-08-05T15:35:54.9621793Z 	at org.gradle.internal.operations.DefaultBuildOperationRunner.execute(DefaultBuildOperationRunner.java:60)
2026-08-05T15:35:54.9622673Z 	at org.gradle.internal.operations.DefaultBuildOperationRunner.call(DefaultBuildOperationRunner.java:54)
2026-08-05T15:35:54.9623616Z 	at org.gradle.internal.execution.steps.ExecuteStep.execute(ExecuteStep.java:134)
2026-08-05T15:35:54.9624268Z 	at org.gradle.internal.execution.steps.ExecuteStep$Mutable.execute(ExecuteStep.java:80)
2026-08-05T15:35:54.9624972Z 	at org.gradle.internal.execution.steps.CancelExecutionStep.execute(CancelExecutionStep.java:42)
2026-08-05T15:35:54.9626054Z 	at org.gradle.internal.execution.steps.TimeoutStep.executeWithoutTimeout(TimeoutStep.java:75)
2026-08-05T15:35:54.9627202Z 	at org.gradle.internal.execution.steps.TimeoutStep.execute(TimeoutStep.java:55)
2026-08-05T15:35:54.9628475Z 	at org.gradle.internal.execution.steps.PreCreateOutputParentsStep.execute(PreCreateOutputParentsStep.java:51)
2026-08-05T15:35:54.9629947Z 	at org.gradle.internal.execution.steps.PreCreateOutputParentsStep.execute(PreCreateOutputParentsStep.java:29)
2026-08-05T15:35:54.9631660Z 	at org.gradle.internal.execution.steps.RemovePreviousOutputsStep.executeMutable(RemovePreviousOutputsStep.java:67)
2026-08-05T15:35:54.9632666Z 	at org.gradle.internal.execution.steps.RemovePreviousOutputsStep.executeMutable(RemovePreviousOutputsStep.java:39)
2026-08-05T15:35:54.9633433Z 	at org.gradle.internal.execution.steps.MutableStep.execute(MutableStep.java:26)
2026-08-05T15:35:54.9634196Z 	at org.gradle.internal.execution.steps.BroadcastChangingOutputsStep.execute(BroadcastChangingOutputsStep.java:42)
2026-08-05T15:35:54.9635091Z 	at org.gradle.internal.execution.steps.BroadcastChangingOutputsStep.execute(BroadcastChangingOutputsStep.java:24)
2026-08-05T15:35:54.9636028Z 	at org.gradle.internal.execution.steps.CaptureOutputsAfterExecutionStep.execute(CaptureOutputsAfterExecutionStep.java:69)
2026-08-05T15:35:54.9637012Z 	at org.gradle.internal.execution.steps.CaptureOutputsAfterExecutionStep.execute(CaptureOutputsAfterExecutionStep.java:46)
2026-08-05T15:35:54.9637973Z 	at org.gradle.internal.execution.steps.ResolveInputChangesStep.executeMutable(ResolveInputChangesStep.java:39)
2026-08-05T15:35:54.9638890Z 	at org.gradle.internal.execution.steps.ResolveInputChangesStep.executeMutable(ResolveInputChangesStep.java:28)
2026-08-05T15:35:54.9639636Z 	at org.gradle.internal.execution.steps.MutableStep.execute(MutableStep.java:26)
2026-08-05T15:35:54.9640337Z 	at org.gradle.internal.execution.steps.BuildCacheStep.executeWithoutCache(BuildCacheStep.java:189)
2026-08-05T15:35:54.9641307Z 	at org.gradle.internal.execution.steps.BuildCacheStep.lambda$execute$1(BuildCacheStep.java:76)
2026-08-05T15:35:54.9641900Z 	at org.gradle.internal.Either$Right.fold(Either.java:176)
2026-08-05T15:35:54.9642430Z 	at org.gradle.internal.execution.caching.CachingState.fold(CachingState.java:62)
2026-08-05T15:35:54.9643311Z 	at org.gradle.internal.execution.steps.BuildCacheStep.execute(BuildCacheStep.java:74)
2026-08-05T15:35:54.9643961Z 	at org.gradle.internal.execution.steps.BuildCacheStep.execute(BuildCacheStep.java:49)
2026-08-05T15:35:54.9644722Z 	at org.gradle.internal.execution.steps.StoreExecutionStateStep.executeMutable(StoreExecutionStateStep.java:46)
2026-08-05T15:35:54.9645600Z 	at org.gradle.internal.execution.steps.StoreExecutionStateStep.executeMutable(StoreExecutionStateStep.java:35)
2026-08-05T15:35:54.9646332Z 	at org.gradle.internal.execution.steps.MutableStep.execute(MutableStep.java:26)
2026-08-05T15:35:54.9647020Z 	at org.gradle.internal.execution.steps.SkipUpToDateStep.executeBecause(SkipUpToDateStep.java:75)
2026-08-05T15:35:54.9647789Z 	at org.gradle.internal.execution.steps.SkipUpToDateStep.lambda$execute$2(SkipUpToDateStep.java:53)
2026-08-05T15:35:54.9648512Z 	at org.gradle.internal.execution.steps.SkipUpToDateStep.execute(SkipUpToDateStep.java:53)
2026-08-05T15:35:54.9649201Z 	at org.gradle.internal.execution.steps.SkipUpToDateStep.execute(SkipUpToDateStep.java:35)
2026-08-05T15:35:54.9650088Z 	at org.gradle.internal.execution.steps.legacy.MarkSnapshottingInputsFinishedStep.execute(MarkSnapshottingInputsFinishedStep.java:37)
2026-08-05T15:35:54.9651691Z 	at org.gradle.internal.execution.steps.legacy.MarkSnapshottingInputsFinishedStep.execute(MarkSnapshottingInputsFinishedStep.java:27)
2026-08-05T15:35:54.9652798Z 	at org.gradle.internal.execution.steps.ResolveMutableCachingStateStep.executeDelegate(ResolveMutableCachingStateStep.java:70)
2026-08-05T15:35:54.9653819Z 	at org.gradle.internal.execution.steps.ResolveMutableCachingStateStep.executeDelegate(ResolveMutableCachingStateStep.java:32)
2026-08-05T15:35:54.9654811Z 	at org.gradle.internal.execution.steps.AbstractResolveCachingStateStep.execute(AbstractResolveCachingStateStep.java:69)
2026-08-05T15:35:54.9655868Z 	at org.gradle.internal.execution.steps.AbstractResolveCachingStateStep.execute(AbstractResolveCachingStateStep.java:37)
2026-08-05T15:35:54.9656766Z 	at org.gradle.internal.execution.steps.ResolveChangesStep.executeMutable(ResolveChangesStep.java:63)
2026-08-05T15:35:54.9657547Z 	at org.gradle.internal.execution.steps.ResolveChangesStep.executeMutable(ResolveChangesStep.java:34)
2026-08-05T15:35:54.9658244Z 	at org.gradle.internal.execution.steps.MutableStep.execute(MutableStep.java:26)
2026-08-05T15:35:54.9658941Z 	at org.gradle.internal.execution.steps.ValidateStep$Mutable.executeDelegate(ValidateStep.java:79)
2026-08-05T15:35:54.9659678Z 	at org.gradle.internal.execution.steps.ValidateStep$Mutable.executeDelegate(ValidateStep.java:65)
2026-08-05T15:35:54.9660359Z 	at org.gradle.internal.execution.steps.ValidateStep.execute(ValidateStep.java:105)
2026-08-05T15:35:54.9661280Z 	at org.gradle.internal.execution.steps.ValidateStep$Mutable.execute(ValidateStep.java:65)
2026-08-05T15:35:54.9662472Z 	at org.gradle.internal.execution.steps.CaptureMutableStateBeforeExecutionStep.executeMutable(CaptureMutableStateBeforeExecutionStep.java:86)
2026-08-05T15:35:54.9663641Z 	at org.gradle.internal.execution.steps.CaptureMutableStateBeforeExecutionStep.execute(CaptureMutableStateBeforeExecutionStep.java:65)
2026-08-05T15:35:54.9664729Z 	at org.gradle.internal.execution.steps.CaptureMutableStateBeforeExecutionStep.execute(CaptureMutableStateBeforeExecutionStep.java:45)
2026-08-05T15:35:54.9665799Z 	at org.gradle.internal.execution.steps.SkipEmptyMutableWorkStep.executeWithNonEmptySources(SkipEmptyMutableWorkStep.java:210)
2026-08-05T15:35:54.9666781Z 	at org.gradle.internal.execution.steps.SkipEmptyMutableWorkStep.executeMutable(SkipEmptyMutableWorkStep.java:90)
2026-08-05T15:35:54.9667679Z 	at org.gradle.internal.execution.steps.SkipEmptyMutableWorkStep.executeMutable(SkipEmptyMutableWorkStep.java:53)
2026-08-05T15:35:54.9668432Z 	at org.gradle.internal.execution.steps.MutableStep.execute(MutableStep.java:26)
2026-08-05T15:35:54.9669278Z 	at org.gradle.internal.execution.steps.legacy.MarkSnapshottingInputsStartedStep.execute(MarkSnapshottingInputsStartedStep.java:38)
2026-08-05T15:35:54.9670505Z 	at org.gradle.internal.execution.steps.LoadPreviousExecutionStateStep.executeMutable(LoadPreviousExecutionStateStep.java:36)
2026-08-05T15:35:54.9671696Z 	at org.gradle.internal.execution.steps.LoadPreviousExecutionStateStep.executeMutable(LoadPreviousExecutionStateStep.java:23)
2026-08-05T15:35:54.9672503Z 	at org.gradle.internal.execution.steps.MutableStep.execute(MutableStep.java:26)
2026-08-05T15:35:54.9673403Z 	at org.gradle.internal.execution.steps.HandleStaleOutputsStep.executeMutable(HandleStaleOutputsStep.java:77)
2026-08-05T15:35:54.9674274Z 	at org.gradle.internal.execution.steps.HandleStaleOutputsStep.executeMutable(HandleStaleOutputsStep.java:43)
2026-08-05T15:35:54.9674998Z 	at org.gradle.internal.execution.steps.MutableStep.execute(MutableStep.java:26)
2026-08-05T15:35:54.9675910Z 	at org.gradle.internal.execution.steps.AssignMutableWorkspaceStep.lambda$executeMutable$0(AssignMutableWorkspaceStep.java:34)
2026-08-05T15:35:54.9676784Z 	at org.gradle.api.internal.tasks.execution.TaskExecution$4.withWorkspace(TaskExecution.java:305)
2026-08-05T15:35:54.9677638Z 	at org.gradle.internal.execution.steps.AssignMutableWorkspaceStep.executeMutable(AssignMutableWorkspaceStep.java:30)
2026-08-05T15:35:54.9678575Z 	at org.gradle.internal.execution.steps.AssignMutableWorkspaceStep.executeMutable(AssignMutableWorkspaceStep.java:21)
2026-08-05T15:35:54.9679495Z 	at org.gradle.internal.execution.steps.MutableStep.execute(MutableStep.java:26)
2026-08-05T15:35:54.9680171Z 	at org.gradle.internal.execution.steps.ChoosePipelineStep.execute(ChoosePipelineStep.java:40)
2026-08-05T15:35:54.9681043Z 	at org.gradle.internal.execution.steps.ChoosePipelineStep.execute(ChoosePipelineStep.java:23)
2026-08-05T15:35:54.9682001Z 	at org.gradle.internal.execution.steps.ExecuteWorkBuildOperationFiringStep.lambda$execute$2(ExecuteWorkBuildOperationFiringStep.java:67)
2026-08-05T15:35:54.9683105Z 	at org.gradle.internal.execution.steps.ExecuteWorkBuildOperationFiringStep.execute(ExecuteWorkBuildOperationFiringStep.java:67)
2026-08-05T15:35:54.9684154Z 	at org.gradle.internal.execution.steps.ExecuteWorkBuildOperationFiringStep.execute(ExecuteWorkBuildOperationFiringStep.java:39)
2026-08-05T15:35:54.9685032Z 	at org.gradle.internal.execution.steps.IdentityCacheStep.execute(IdentityCacheStep.java:46)
2026-08-05T15:35:54.9685740Z 	at org.gradle.internal.execution.steps.IdentityCacheStep.execute(IdentityCacheStep.java:34)
2026-08-05T15:35:54.9686417Z 	at org.gradle.internal.execution.steps.IdentifyStep.execute(IdentifyStep.java:56)
2026-08-05T15:35:54.9687046Z 	at org.gradle.internal.execution.steps.IdentifyStep.execute(IdentifyStep.java:38)
2026-08-05T15:35:54.9687755Z 	at org.gradle.internal.execution.impl.DefaultExecutionEngine$1.execute(DefaultExecutionEngine.java:68)
2026-08-05T15:35:54.9688662Z 	at org.gradle.api.internal.tasks.execution.ExecuteActionsTaskExecuter.executeIfValid(ExecuteActionsTaskExecuter.java:132)
2026-08-05T15:35:54.9689312Z 	... 30 more
2026-08-05T15:35:54.9689458Z 
2026-08-05T15:35:54.9689462Z 
2026-08-05T15:35:54.9689576Z BUILD FAILED in 7m 19s
2026-08-05T15:35:54.9690160Z Finished generating test XML results (0.029 secs) into: /home/runner/work/sirix/sirix/bundles/sirix-query/build/test-results/test
2026-08-05T15:35:54.9691239Z gradle/actions: Writing build results to /home/runner/work/_temp/.gradle-actions/build-results/__run-1785943722169.json
2026-08-05T15:35:54.9691699Z 
2026-08-05T15:35:54.9692112Z [Incubating] Problems report is available at: file:///home/runner/work/sirix/sirix/build/reports/problems/problems-report.html
2026-08-05T15:35:54.9692595Z 
2026-08-05T15:35:54.9692874Z Deprecated Gradle features were used in this build, making it incompatible with Gradle 10.
2026-08-05T15:35:54.9693241Z 
2026-08-05T15:35:54.9693665Z You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.
2026-08-05T15:35:54.9694168Z 
2026-08-05T15:35:54.9709057Z For more on this, please refer to https://docs.gradle.org/9.6.1/userguide/command_line_interface.html#sec:command_line_warnings in the Gradle documentation.
2026-08-05T15:35:54.9710179Z 29 actionable tasks: 29 executed
2026-08-05T15:35:55.3735484Z ##[error]Process completed with exit code 1.
2026-08-05T15:35:55.3875200Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-08-05T15:35:55.3876416Z Post job cleanup.
2026-08-05T15:35:55.6496529Z In post-action step
2026-08-05T15:35:55.6507384Z Cache is read-only: will not save state for use in subsequent builds.
2026-08-05T15:35:55.6513581Z Generating Job Summary
2026-08-05T15:35:55.6531034Z Completed post-action step
2026-08-05T15:35:55.6654283Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-08-05T15:35:55.6655559Z Post job cleanup.
2026-08-05T15:35:55.8135237Z (node:4332) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-08-05T15:35:55.8136030Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-08-05T15:35:55.8368499Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-08-05T15:35:55.8369813Z Post job cleanup.
2026-08-05T15:35:55.9321333Z [command]/usr/bin/git version
2026-08-05T15:35:55.9371566Z git version 2.54.0
2026-08-05T15:35:55.9414503Z Temporarily overriding HOME='/home/runner/work/_temp/c2e18fa2-f49f-4a05-bce0-7731212602c1' before making global git config changes
2026-08-05T15:35:55.9418033Z Adding repository directory to the temporary git global config as a safe directory
2026-08-05T15:35:55.9421317Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/sirix/sirix
2026-08-05T15:35:55.9473940Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-08-05T15:35:55.9527296Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-08-05T15:35:55.9870444Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-08-05T15:35:55.9910658Z http.https://github.com/.extraheader
2026-08-05T15:35:55.9924258Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-08-05T15:35:55.9979837Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-08-05T15:35:56.0324645Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-08-05T15:35:56.0380102Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-08-05T15:35:56.0847270Z Cleaning up orphan processes
2026-08-05T15:35:56.1164918Z Terminate orphan process: pid (2520) (java)
2026-08-05T15:35:56.1192464Z Terminate orphan process: pid (2692) (java)
2026-08-05T15:35:56.1202395Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/cache/restore@v4, actions/checkout@v4, actions/setup-java@v4, gradle/actions/setup-gradle@v4. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 35. `spiculedata__saiku__079996412627.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/spiculedata__saiku__079996412627.txt` (authoritative; read this, not the excerpt)
- **Repository**: `spiculedata/saiku`
- **Content hash (sha256, first 16)**: `30335a7a876eab4b`
- **Body size**: 75,789 bytes, 753 lines
- **Excerpt**: final 120 of 753 lines, content-blind

```text
2026-06-07T22:18:07.7274480Z [INFO] 
2026-06-07T22:18:07.7274720Z [INFO] Results:
2026-06-07T22:18:07.7276660Z [INFO] 
2026-06-07T22:18:07.7277090Z [WARNING] Tests run: 541, Failures: 0, Errors: 0, Skipped: 1
2026-06-07T22:18:07.7277370Z [INFO] 
2026-06-07T22:18:07.7312400Z [INFO] 
2026-06-07T22:18:07.7316870Z [INFO] --- jar:3.5.0:jar (default-jar) @ saiku-service ---
2026-06-07T22:18:07.7617050Z [INFO] Building jar: /Users/runner/work/saiku/saiku/saiku-core/saiku-service/target/saiku-service-4.4.0.jar
2026-06-07T22:18:07.8372150Z [INFO] 
2026-06-07T22:18:07.8416530Z [INFO] --- source:2.3:jar-no-fork (attach-sources) @ saiku-service ---
2026-06-07T22:18:07.8743690Z [INFO] Building jar: /Users/runner/work/saiku/saiku/saiku-core/saiku-service/target/saiku-service-4.4.0-sources.jar
2026-06-07T22:18:08.0067080Z [INFO] 
2026-06-07T22:18:08.0067690Z [INFO] --- source:2.3:test-jar-no-fork (attach-sources) @ saiku-service ---
2026-06-07T22:18:08.0188700Z [INFO] Building jar: /Users/runner/work/saiku/saiku/saiku-core/saiku-service/target/saiku-service-4.4.0-test-sources.jar
2026-06-07T22:18:08.0561990Z [INFO] 
2026-06-07T22:18:08.0562480Z [INFO] --- spotless:2.46.1:check (spotless-check) @ saiku-service ---
2026-06-07T22:18:08.0906900Z [INFO] Index file does not exist. Fallback to an empty index
2026-06-07T22:18:11.8823700Z [INFO] Spotless.Java is keeping 358 files clean - 2 needs changes to be clean, 356 were already clean, 0 were skipped because caching determined they were already clean
2026-06-07T22:18:11.9469110Z [INFO] ------------------------------------------------------------------------
2026-06-07T22:18:11.9571600Z [INFO] Reactor Summary for Saiku Module Project 4.4.0:
2026-06-07T22:18:11.9675120Z [INFO] 
2026-06-07T22:18:11.9768580Z [INFO] Saiku BOM .......................................... SUCCESS [  0.001 s]
2026-06-07T22:18:11.9842840Z [INFO] Saiku Module Project ............................... SUCCESS [  0.879 s]
2026-06-07T22:18:11.9873500Z [INFO] saiku - core libraries ............................. SUCCESS [  0.027 s]
2026-06-07T22:18:11.9880790Z [INFO] saiku olap util .................................... SUCCESS [  3.174 s]
2026-06-07T22:18:11.9899050Z [INFO] saiku - semantic layer ............................. SUCCESS [  2.306 s]
2026-06-07T22:18:11.9928550Z [INFO] saiku - services ................................... FAILURE [ 19.592 s]
2026-06-07T22:18:11.9931160Z [INFO] saiku - web ........................................ SKIPPED
2026-06-07T22:18:11.9932580Z [INFO] saiku - webapp ..................................... SKIPPED
2026-06-07T22:18:11.9933810Z [INFO] saiku - launcher ................................... SKIPPED
2026-06-07T22:18:11.9937340Z [INFO] ------------------------------------------------------------------------
2026-06-07T22:18:11.9937750Z [INFO] BUILD FAILURE
2026-06-07T22:18:11.9938110Z [INFO] ------------------------------------------------------------------------
2026-06-07T22:18:11.9939050Z [INFO] Total time:  27.069 s
2026-06-07T22:18:11.9939400Z [INFO] Finished at: 2026-06-07T22:18:11Z
2026-06-07T22:18:11.9939810Z [INFO] ------------------------------------------------------------------------
2026-06-07T22:18:11.9940590Z [ERROR] Failed to execute goal com.diffplug.spotless:spotless-maven-plugin:2.46.1:check (spotless-check) on project saiku-service: The following files had format violations:
2026-06-07T22:18:11.9941270Z [ERROR]     src/test/java/org/saiku/olap/util/TimeCalcParserTest.java
2026-06-07T22:18:11.9942810Z [ERROR]         @@ -26,28 +26,27 @@
2026-06-07T22:18:11.9948180Z [ERROR]          ·*··most·assertions·feed·a·{@link·Document}·parsed·from·an·in-memory·string.·*/
2026-06-07T22:18:11.9955590Z [ERROR]          public·class·TimeCalcParserTest·{
2026-06-07T22:18:11.9956210Z [ERROR]          
2026-06-07T22:18:11.9956570Z [ERROR]         -····private·static·final·String·BANK_SCHEMA_FRAGMENT·=
2026-06-07T22:18:11.9957160Z [ERROR]         -············"<?xml·version=\"1.0\"·encoding=\"UTF-8\"?>\n"
2026-06-07T22:18:11.9957540Z [ERROR]         -····················+·"<Schema·name='Bank'>\n"
2026-06-07T22:18:11.9957900Z [ERROR]         -····················+·"··<Cube·name='Monthly·Revenue'>\n"
2026-06-07T22:18:11.9958270Z [ERROR]         -····················+·"····<MeasureGroups/>\n"
2026-06-07T22:18:11.9958630Z [ERROR]         -····················+·"····<TimeCalcs>\n"
2026-06-07T22:18:11.9959120Z [ERROR]         -····················+·"······<TimeCalc·name='Revenue·YoY'·type='yoy'·measure='Revenue'\n"
2026-06-07T22:18:11.9960150Z [ERROR]         -····················+·"················timeDimension='Calendar'·formatString='0.0%'/>\n"
2026-06-07T22:18:11.9960790Z [ERROR]         -····················+·"······<TimeCalc·name='Revenue·PoP'·type='pop'·measure='Revenue'\n"
2026-06-07T22:18:11.9961350Z [ERROR]         -····················+·"················timeDimension='Calendar'·formatString='0.0%'/>\n"
2026-06-07T22:18:11.9961880Z [ERROR]         -····················+·"······<TimeCalc·name='Revenue·YTD'·type='ytd'·measure='Revenue'\n"
2026-06-07T22:18:11.9962420Z [ERROR]         -····················+·"················timeDimension='Calendar'·formatString='#,###'/>\n"
2026-06-07T22:18:11.9963360Z [ERROR]         -····················+·"······<TimeCalc·name='Revenue·R3'·type='rolling'·measure='Revenue'\n"
2026-06-07T22:18:11.9963910Z [ERROR]         -····················+·"················timeDimension='Calendar'·window='3'·function='avg'\n"
2026-06-07T22:18:11.9964390Z [ERROR]         -····················+·"················formatString='#,###'/>\n"
2026-06-07T22:18:11.9964750Z [ERROR]         -····················+·"····</TimeCalcs>\n"
2026-06-07T22:18:11.9965080Z [ERROR]         -····················+·"··</Cube>\n"
2026-06-07T22:18:11.9965400Z [ERROR]         -····················+·"··<Cube·name='Accounts'>\n"
2026-06-07T22:18:11.9965980Z [ERROR]         -····················+·"····<!--·no·TimeCalcs·here·—·parser·must·return·empty·list·for·this·cube·-->\n"
2026-06-07T22:18:11.9966460Z [ERROR]         -····················+·"····<MeasureGroups/>\n"
2026-06-07T22:18:11.9966780Z [ERROR]         -····················+·"··</Cube>\n"
2026-06-07T22:18:11.9967080Z [ERROR]         -····················+·"</Schema>\n";
2026-06-07T22:18:11.9967560Z [ERROR]         +····private·static·final·String·BANK_SCHEMA_FRAGMENT·=·"<?xml·version=\"1.0\"·encoding=\"UTF-8\"?>\n"
2026-06-07T22:18:11.9968050Z [ERROR]         +············+·"<Schema·name='Bank'>\n"
2026-06-07T22:18:11.9968400Z [ERROR]         +············+·"··<Cube·name='Monthly·Revenue'>\n"
2026-06-07T22:18:11.9970810Z [ERROR]         +············+·"····<MeasureGroups/>\n"
2026-06-07T22:18:11.9971650Z [ERROR]         +············+·"····<TimeCalcs>\n"
2026-06-07T22:18:11.9973170Z [ERROR]         +············+·"······<TimeCalc·name='Revenue·YoY'·type='yoy'·measure='Revenue'\n"
2026-06-07T22:18:11.9974560Z [ERROR]         +············+·"················timeDimension='Calendar'·formatString='0.0%'/>\n"
2026-06-07T22:18:11.9976460Z [ERROR]         +············+·"······<TimeCalc·name='Revenue·PoP'·type='pop'·measure='Revenue'\n"
2026-06-07T22:18:11.9977910Z [ERROR]         +············+·"················timeDimension='Calendar'·formatString='0.0%'/>\n"
2026-06-07T22:18:11.9979500Z [ERROR]         +············+·"······<TimeCalc·name='Revenue·YTD'·type='ytd'·measure='Revenue'\n"
2026-06-07T22:18:11.9980870Z [ERROR]         +············+·"················timeDimension='Calendar'·formatString='#,###'/>\n"
2026-06-07T22:18:11.9982260Z [ERROR]         +············+·"······<TimeCalc·name='Revenue·R3'·type='rolling'·measure='Revenue'\n"
2026-06-07T22:18:11.9983690Z [ERROR]         +············+·"················timeDimension='Calendar'·window='3'·function='avg'\n"
2026-06-07T22:18:11.9985320Z [ERROR]         +············+·"················formatString='#,###'/>\n"
2026-06-07T22:18:11.9985650Z [ERROR]         +············+·"····</TimeCalcs>\n"
2026-06-07T22:18:11.9985950Z [ERROR]         +············+·"··</Cube>\n"
2026-06-07T22:18:11.9986250Z [ERROR]         +············+·"··<Cube·name='Accounts'>\n"
2026-06-07T22:18:11.9986900Z [ERROR]         +············+·"····<!--·no·TimeCalcs·here·—·parser·must·return·empty·list·for·this·cube·-->\n"
2026-06-07T22:18:11.9987340Z [ERROR]         +············+·"····<MeasureGroups/>\n"
2026-06-07T22:18:11.9987630Z [ERROR]         +············+·"··</Cube>\n"
2026-06-07T22:18:11.9987900Z [ERROR]         +············+·"</Schema>\n";
2026-06-07T22:18:11.9988100Z [ERROR]          
2026-06-07T22:18:11.9988850Z [ERROR]          ····private·static·Document·doc(String·xml)·throws·IOException,·SAXException,·ParserConfigurationException·{
2026-06-07T22:18:11.9989340Z [ERROR]     ... (11 more lines that didn't fit)
2026-06-07T22:18:11.9989600Z [ERROR] Violations also present in:
2026-06-07T22:18:11.9989900Z [ERROR]     src/main/java/org/saiku/olap/discover/OlapMetaExplorer.java
2026-06-07T22:18:11.9990250Z [ERROR] Run 'mvn spotless:apply' to fix these violations.
2026-06-07T22:18:11.9990500Z [ERROR] -> [Help 1]
2026-06-07T22:18:11.9990650Z [ERROR] 
2026-06-07T22:18:11.9990910Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-06-07T22:18:11.9991310Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-06-07T22:18:11.9992380Z [ERROR] 
2026-06-07T22:18:11.9993320Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-06-07T22:18:11.9995660Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoExecutionException
2026-06-07T22:18:11.9996620Z [ERROR] 
2026-06-07T22:18:11.9997310Z [ERROR] After correcting the problems, you can resume the build with the command
2026-06-07T22:18:11.9998570Z [ERROR]   mvn <args> -rf :saiku-service
2026-06-07T22:18:12.0527370Z ##[error]Process completed with exit code 1.
2026-06-07T22:18:12.0757080Z Post job cleanup.
2026-06-07T22:18:12.5317390Z Post job cleanup.
2026-06-07T22:18:12.6674130Z [command]/opt/homebrew/bin/git version
2026-06-07T22:18:12.6918600Z git version 2.54.0
2026-06-07T22:18:12.6959350Z Copying '/Users/runner/.gitconfig' to '/Users/runner/work/_temp/cebcdf44-3b0c-486b-9966-eddc3ec4c898/.gitconfig'
2026-06-07T22:18:12.6973860Z Temporarily overriding HOME='/Users/runner/work/_temp/cebcdf44-3b0c-486b-9966-eddc3ec4c898' before making global git config changes
2026-06-07T22:18:12.6974800Z Adding repository directory to the temporary git global config as a safe directory
2026-06-07T22:18:12.6976620Z [command]/opt/homebrew/bin/git config --global --add safe.directory /Users/runner/work/saiku/saiku
2026-06-07T22:18:12.7089040Z [command]/opt/homebrew/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-06-07T22:18:12.7151440Z [command]/opt/homebrew/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-06-07T22:18:12.8191410Z [command]/opt/homebrew/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-06-07T22:18:12.8255500Z http.https://github.com/.extraheader
2026-06-07T22:18:12.8316540Z [command]/opt/homebrew/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-06-07T22:18:12.8386290Z [command]/opt/homebrew/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-06-07T22:18:12.9894190Z [command]/opt/homebrew/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-06-07T22:18:13.0206280Z [command]/opt/homebrew/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-06-07T22:18:13.1789140Z Cleaning up orphan processes
2026-06-07T22:18:14.0651220Z ##[warning]Node.js 20 actions are deprecated. The following actions are running on Node.js 20 and may not work as expected: actions/checkout@v4, actions/setup-java@v4. Actions will be forced to run with Node.js 24 by default starting June 16th, 2026. Node.js 20 will be removed from the runner on September 16th, 2026. Please check if updated versions of these actions are available that support Node.js 24. To opt into Node.js 24 now, set the FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true environment variable on the runner or in your workflow file. Once Node.js 24 becomes the default, you can temporarily opt out by setting ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 36. `thealgorithms__java__079347942021.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/thealgorithms__java__079347942021.txt` (authoritative; read this, not the excerpt)
- **Repository**: `thealgorithms/java`
- **Content hash (sha256, first 16)**: `4e65ba5f08664755`
- **Body size**: 605,821 bytes, 6,740 lines
- **Excerpt**: final 120 of 6,740 lines, content-blind

```text
2026-06-03T16:51:02.8688566Z Progress (1): 57/674 kB
2026-06-03T16:51:02.8691409Z Progress (1): 73/674 kB
2026-06-03T16:51:02.8692008Z Progress (1): 90/674 kB
2026-06-03T16:51:02.8692616Z Progress (1): 106/674 kB
2026-06-03T16:51:02.8697778Z Progress (1): 122/674 kB
2026-06-03T16:51:02.8699151Z Progress (1): 139/674 kB
2026-06-03T16:51:02.8700674Z Progress (1): 155/674 kB
2026-06-03T16:51:02.8701533Z Progress (1): 172/674 kB
2026-06-03T16:51:02.8707712Z Progress (1): 188/674 kB
2026-06-03T16:51:02.8709597Z Progress (1): 204/674 kB
2026-06-03T16:51:02.8709888Z Progress (1): 221/674 kB
2026-06-03T16:51:02.8716500Z Progress (1): 237/674 kB
2026-06-03T16:51:02.8719671Z Progress (1): 253/674 kB
2026-06-03T16:51:02.8720115Z Progress (1): 262/674 kB
2026-06-03T16:51:02.8720349Z Progress (1): 279/674 kB
2026-06-03T16:51:02.8720577Z Progress (1): 295/674 kB
2026-06-03T16:51:02.8727579Z Progress (1): 311/674 kB
2026-06-03T16:51:02.8728505Z Progress (1): 328/674 kB
2026-06-03T16:51:02.8729064Z Progress (1): 344/674 kB
2026-06-03T16:51:02.8736515Z Progress (1): 360/674 kB
2026-06-03T16:51:02.8737015Z Progress (2): 360/674 kB | 7.7/12 kB
2026-06-03T16:51:02.8737476Z Progress (2): 360/674 kB | 7.7/12 kB
2026-06-03T16:51:02.8737913Z Progress (2): 360/674 kB | 12 kB    
2026-06-03T16:51:02.8738334Z                                 
2026-06-03T16:51:02.8739459Z Downloaded from central: https://repo.maven.apache.org/maven2/org/codehaus/plexus/plexus-i18n/1.0-beta-10/plexus-i18n-1.0-beta-10.jar (12 kB at 19 kB/s)
2026-06-03T16:51:02.8744649Z Progress (1): 377/674 kB
2026-06-03T16:51:02.8745291Z Progress (1): 393/674 kB
2026-06-03T16:51:02.8746221Z Progress (1): 410/674 kB
2026-06-03T16:51:02.8751653Z Progress (1): 426/674 kB
2026-06-03T16:51:02.8752707Z Progress (1): 442/674 kB
2026-06-03T16:51:02.8753397Z Progress (1): 459/674 kB
2026-06-03T16:51:02.8754312Z Progress (1): 475/674 kB
2026-06-03T16:51:02.8755664Z Progress (1): 492/674 kB
2026-06-03T16:51:02.8756830Z Progress (1): 508/674 kB
2026-06-03T16:51:02.8757894Z Progress (1): 524/674 kB
2026-06-03T16:51:02.8763865Z Progress (1): 541/674 kB
2026-06-03T16:51:02.8764821Z Progress (1): 557/674 kB
2026-06-03T16:51:02.8767139Z Progress (1): 573/674 kB
2026-06-03T16:51:02.8767620Z Progress (1): 590/674 kB
2026-06-03T16:51:02.8851667Z Progress (1): 606/674 kB
2026-06-03T16:51:02.8859810Z Progress (1): 623/674 kB
2026-06-03T16:51:02.8860488Z Progress (2): 623/674 kB | 7.7/57 kB
2026-06-03T16:51:02.8868229Z Progress (2): 623/674 kB | 16/57 kB 
2026-06-03T16:51:02.8872203Z Progress (2): 623/674 kB | 32/57 kB
2026-06-03T16:51:02.8873202Z Progress (2): 623/674 kB | 48/57 kB
2026-06-03T16:51:02.8873686Z Progress (2): 623/674 kB | 57 kB   
2026-06-03T16:51:02.8874139Z Progress (2): 639/674 kB | 57 kB
2026-06-03T16:51:02.8874814Z                                 
2026-06-03T16:51:02.8876003Z Downloaded from central: https://repo.maven.apache.org/maven2/javax/activation/javax.activation-api/1.2.0/javax.activation-api-1.2.0.jar (57 kB at 90 kB/s)
2026-06-03T16:51:02.8877218Z Progress (1): 655/674 kB
2026-06-03T16:51:02.8877603Z Progress (1): 672/674 kB
2026-06-03T16:51:02.8877983Z Progress (1): 674 kB    
2026-06-03T16:51:02.8878340Z                     
2026-06-03T16:51:02.8879653Z Downloaded from central: https://repo.maven.apache.org/maven2/org/apache/commons/commons-lang3/3.17.0/commons-lang3-3.17.0.jar (674 kB at 1.1 MB/s)
2026-06-03T16:51:02.8966497Z Progress (1): 7.7/128 kB
2026-06-03T16:51:02.8967486Z Progress (1): 16/128 kB 
2026-06-03T16:51:02.8968080Z Progress (1): 28/128 kB
2026-06-03T16:51:02.8968678Z Progress (1): 44/128 kB
2026-06-03T16:51:02.8973625Z Progress (1): 61/128 kB
2026-06-03T16:51:02.8974040Z Progress (1): 77/128 kB
2026-06-03T16:51:02.8974684Z Progress (1): 82/128 kB
2026-06-03T16:51:02.8975062Z Progress (1): 98/128 kB
2026-06-03T16:51:02.8975436Z Progress (1): 115/128 kB
2026-06-03T16:51:02.8975820Z Progress (1): 128 kB    
2026-06-03T16:51:02.8976177Z                     
2026-06-03T16:51:02.8977142Z Downloaded from central: https://repo.maven.apache.org/maven2/javax/xml/bind/jaxb-api/2.3.1/jaxb-api-2.3.1.jar (128 kB at 200 kB/s)
2026-06-03T16:51:10.8298802Z [INFO] Starting audit...
2026-06-03T16:51:10.8300540Z [ERROR] /home/runner/work/Java/Java/src/test/java/com/thealgorithms/datastructures/lists/MergeSortedArrayListTest.java:1: File does not end with a newline. [NewlineAtEndOfFile]
2026-06-03T16:51:10.8302221Z Audit done.
2026-06-03T16:51:10.8303128Z [INFO] There is 1 error reported by Checkstyle 13.5.0 with checkstyle.xml ruleset.
2026-06-03T16:51:10.8681695Z [ERROR] src/test/java/com/thealgorithms/datastructures/lists/MergeSortedArrayListTest.java:[1] (misc) NewlineAtEndOfFile: File does not end with a newline.
2026-06-03T16:51:10.8685139Z [INFO] ------------------------------------------------------------------------
2026-06-03T16:51:10.8685789Z [INFO] BUILD FAILURE
2026-06-03T16:51:10.8686301Z [INFO] ------------------------------------------------------------------------
2026-06-03T16:51:10.8686945Z [INFO] Total time:  17.224 s
2026-06-03T16:51:10.8695597Z [INFO] Finished at: 2026-06-03T16:51:10Z
2026-06-03T16:51:10.8696487Z [INFO] ------------------------------------------------------------------------
2026-06-03T16:51:10.8698344Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-checkstyle-plugin:3.6.0:check (default-cli) on project Java: You have 1 Checkstyle violation. -> [Help 1]
2026-06-03T16:51:10.8699814Z [ERROR] 
2026-06-03T16:51:10.8700572Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-06-03T16:51:10.8701661Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-06-03T16:51:10.8702478Z [ERROR] 
2026-06-03T16:51:10.8703338Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-06-03T16:51:10.8704859Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
2026-06-03T16:51:10.9123644Z ##[error]Process completed with exit code 1.
2026-06-03T16:51:10.9213353Z Post job cleanup.
2026-06-03T16:51:11.0552631Z Post job cleanup.
2026-06-03T16:51:11.1480525Z [command]/usr/bin/git version
2026-06-03T16:51:11.1520211Z git version 2.54.0
2026-06-03T16:51:11.1588010Z Copying '/home/runner/.gitconfig' to '/home/runner/work/_temp/ebbe9b9a-8799-4ce7-bb3b-9d7d0f7468e3/.gitconfig'
2026-06-03T16:51:11.1598297Z Temporarily overriding HOME='/home/runner/work/_temp/ebbe9b9a-8799-4ce7-bb3b-9d7d0f7468e3' before making global git config changes
2026-06-03T16:51:11.1599736Z Adding repository directory to the temporary git global config as a safe directory
2026-06-03T16:51:11.1605045Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/Java/Java
2026-06-03T16:51:11.1635136Z Removing SSH command configuration
2026-06-03T16:51:11.1641837Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-06-03T16:51:11.1675651Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-06-03T16:51:11.1895874Z Removing HTTP extra header
2026-06-03T16:51:11.1900372Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-06-03T16:51:11.1934183Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-06-03T16:51:11.2147782Z Removing includeIf entries pointing to credentials config files
2026-06-03T16:51:11.2153618Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-06-03T16:51:11.2177868Z includeif.gitdir:/home/runner/work/Java/Java/.git.path
2026-06-03T16:51:11.2178809Z includeif.gitdir:/home/runner/work/Java/Java/.git/worktrees/*.path
2026-06-03T16:51:11.2179518Z includeif.gitdir:/github/workspace/.git.path
2026-06-03T16:51:11.2180081Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-06-03T16:51:11.2187462Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/Java/Java/.git.path
2026-06-03T16:51:11.2211298Z /home/runner/work/_temp/git-credentials-9f8ebcab-60f8-4c02-99a4-35b513c3e6ad.config
2026-06-03T16:51:11.2222052Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/Java/Java/.git.path /home/runner/work/_temp/git-credentials-9f8ebcab-60f8-4c02-99a4-35b513c3e6ad.config
2026-06-03T16:51:11.2259358Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/Java/Java/.git/worktrees/*.path
2026-06-03T16:51:11.2280626Z /home/runner/work/_temp/git-credentials-9f8ebcab-60f8-4c02-99a4-35b513c3e6ad.config
2026-06-03T16:51:11.2290015Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/Java/Java/.git/worktrees/*.path /home/runner/work/_temp/git-credentials-9f8ebcab-60f8-4c02-99a4-35b513c3e6ad.config
2026-06-03T16:51:11.2320451Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-06-03T16:51:11.2340695Z /github/runner_temp/git-credentials-9f8ebcab-60f8-4c02-99a4-35b513c3e6ad.config
2026-06-03T16:51:11.2349679Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git.path /github/runner_temp/git-credentials-9f8ebcab-60f8-4c02-99a4-35b513c3e6ad.config
2026-06-03T16:51:11.2381472Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-06-03T16:51:11.2426455Z /github/runner_temp/git-credentials-9f8ebcab-60f8-4c02-99a4-35b513c3e6ad.config
2026-06-03T16:51:11.2436032Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path /github/runner_temp/git-credentials-9f8ebcab-60f8-4c02-99a4-35b513c3e6ad.config
2026-06-03T16:51:11.2467925Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-06-03T16:51:11.2686599Z Removing credentials config '/home/runner/work/_temp/git-credentials-9f8ebcab-60f8-4c02-99a4-35b513c3e6ad.config'
2026-06-03T16:51:11.2827202Z Cleaning up orphan processes
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 37. `unicode-org__cldr__077741081038.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/unicode-org__cldr__077741081038.txt` (authoritative; read this, not the excerpt)
- **Repository**: `unicode-org/cldr`
- **Content hash (sha256, first 16)**: `9eb129f05fb52129`
- **Body size**: 1,782,443 bytes, 12,017 lines
- **Excerpt**: final 120 of 12,017 lines, content-blind

```text
2026-05-25T16:37:16.6382964Z 	at org.junit.jupiter.engine.execution.InvocationInterceptorChain.invoke(InvocationInterceptorChain.java:37)
2026-05-25T16:37:16.6384292Z 	at org.junit.jupiter.engine.execution.ExecutableInvoker.invoke(ExecutableInvoker.java:104)
2026-05-25T16:37:16.6385486Z 	at org.junit.jupiter.engine.execution.ExecutableInvoker.invoke(ExecutableInvoker.java:98)
2026-05-25T16:37:16.6386890Z 	at org.junit.jupiter.engine.descriptor.TestMethodTestDescriptor.lambda$invokeTestMethod$7(TestMethodTestDescriptor.java:214)
2026-05-25T16:37:16.6388386Z 	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
2026-05-25T16:37:16.6389855Z 	at org.junit.jupiter.engine.descriptor.TestMethodTestDescriptor.invokeTestMethod(TestMethodTestDescriptor.java:210)
2026-05-25T16:37:16.6391328Z 	at org.junit.jupiter.engine.descriptor.TestMethodTestDescriptor.execute(TestMethodTestDescriptor.java:135)
2026-05-25T16:37:16.6392899Z 	at org.junit.jupiter.engine.descriptor.TestMethodTestDescriptor.execute(TestMethodTestDescriptor.java:66)
2026-05-25T16:37:16.6394304Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$6(NodeTestTask.java:151)
2026-05-25T16:37:16.6395867Z 	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
2026-05-25T16:37:16.6397248Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$8(NodeTestTask.java:141)
2026-05-25T16:37:16.6398412Z 	at org.junit.platform.engine.support.hierarchical.Node.around(Node.java:137)
2026-05-25T16:37:16.6399717Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$9(NodeTestTask.java:139)
2026-05-25T16:37:16.6401138Z 	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
2026-05-25T16:37:16.6402709Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.executeRecursively(NodeTestTask.java:138)
2026-05-25T16:37:16.6404025Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.execute(NodeTestTask.java:95)
2026-05-25T16:37:16.6404998Z 	at java.base/java.util.ArrayList.forEach(ArrayList.java:1541)
2026-05-25T16:37:16.6406488Z 	at org.junit.platform.engine.support.hierarchical.SameThreadHierarchicalTestExecutorService.invokeAll(SameThreadHierarchicalTestExecutorService.java:41)
2026-05-25T16:37:16.6408355Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$6(NodeTestTask.java:155)
2026-05-25T16:37:16.6409768Z 	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
2026-05-25T16:37:16.6411212Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$8(NodeTestTask.java:141)
2026-05-25T16:37:16.6412648Z 	at org.junit.platform.engine.support.hierarchical.Node.around(Node.java:137)
2026-05-25T16:37:16.6414197Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$9(NodeTestTask.java:139)
2026-05-25T16:37:16.6415642Z 	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
2026-05-25T16:37:16.6417088Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.executeRecursively(NodeTestTask.java:138)
2026-05-25T16:37:16.6418407Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.execute(NodeTestTask.java:95)
2026-05-25T16:37:16.6419365Z 	at java.base/java.util.ArrayList.forEach(ArrayList.java:1541)
2026-05-25T16:37:16.6420837Z 	at org.junit.platform.engine.support.hierarchical.SameThreadHierarchicalTestExecutorService.invokeAll(SameThreadHierarchicalTestExecutorService.java:41)
2026-05-25T16:37:16.6422990Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$6(NodeTestTask.java:155)
2026-05-25T16:37:16.6424451Z 	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
2026-05-25T16:37:16.6425852Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$8(NodeTestTask.java:141)
2026-05-25T16:37:16.6427070Z 	at org.junit.platform.engine.support.hierarchical.Node.around(Node.java:137)
2026-05-25T16:37:16.6428264Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$9(NodeTestTask.java:139)
2026-05-25T16:37:16.6429668Z 	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
2026-05-25T16:37:16.6431026Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.executeRecursively(NodeTestTask.java:138)
2026-05-25T16:37:16.6432468Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.execute(NodeTestTask.java:95)
2026-05-25T16:37:16.6434135Z 	at org.junit.platform.engine.support.hierarchical.SameThreadHierarchicalTestExecutorService.submit(SameThreadHierarchicalTestExecutorService.java:35)
2026-05-25T16:37:16.6435967Z 	at org.junit.platform.engine.support.hierarchical.HierarchicalTestExecutor.execute(HierarchicalTestExecutor.java:57)
2026-05-25T16:37:16.6437474Z 	at org.junit.platform.engine.support.hierarchical.HierarchicalTestEngine.execute(HierarchicalTestEngine.java:54)
2026-05-25T16:37:16.6439175Z 	at org.junit.platform.launcher.core.EngineExecutionOrchestrator.execute(EngineExecutionOrchestrator.java:107)
2026-05-25T16:37:16.6440668Z 	at org.junit.platform.launcher.core.EngineExecutionOrchestrator.execute(EngineExecutionOrchestrator.java:88)
2026-05-25T16:37:16.6442407Z 	at org.junit.platform.launcher.core.EngineExecutionOrchestrator.lambda$execute$0(EngineExecutionOrchestrator.java:54)
2026-05-25T16:37:16.6444248Z 	at org.junit.platform.launcher.core.EngineExecutionOrchestrator.withInterceptedStreams(EngineExecutionOrchestrator.java:67)
2026-05-25T16:37:16.6445832Z 	at org.junit.platform.launcher.core.EngineExecutionOrchestrator.execute(EngineExecutionOrchestrator.java:52)
2026-05-25T16:37:16.6447094Z 	at org.junit.platform.launcher.core.DefaultLauncher.execute(DefaultLauncher.java:114)
2026-05-25T16:37:16.6448160Z 	at org.junit.platform.launcher.core.DefaultLauncher.execute(DefaultLauncher.java:86)
2026-05-25T16:37:16.6449478Z 	at org.junit.platform.launcher.core.DefaultLauncherSession$DelegatingLauncher.execute(DefaultLauncherSession.java:86)
2026-05-25T16:37:16.6450811Z 	at org.apache.maven.surefire.junitplatform.LazyLauncher.execute(LazyLauncher.java:56)
2026-05-25T16:37:16.6452303Z 	at org.apache.maven.surefire.junitplatform.JUnitPlatformProvider.execute(JUnitPlatformProvider.java:184)
2026-05-25T16:37:16.6453795Z 	at org.apache.maven.surefire.junitplatform.JUnitPlatformProvider.invokeAllTests(JUnitPlatformProvider.java:148)
2026-05-25T16:37:16.6455282Z 	at org.apache.maven.surefire.junitplatform.JUnitPlatformProvider.invoke(JUnitPlatformProvider.java:122)
2026-05-25T16:37:16.6456605Z 	at org.apache.maven.surefire.booter.ForkedBooter.runSuitesInProcess(ForkedBooter.java:385)
2026-05-25T16:37:16.6457703Z 	at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
2026-05-25T16:37:16.6458662Z 	at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
2026-05-25T16:37:16.6459608Z 	at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)
2026-05-25T16:37:16.6460173Z 
2026-05-25T16:37:16.6460445Z [INFO] Running org.unicode.cldr.json.LdmlConvertRulesTest
2026-05-25T16:37:16.6461465Z [INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.004 s -- in org.unicode.cldr.json.LdmlConvertRulesTest
2026-05-25T16:37:25.1269431Z [INFO] 
2026-05-25T16:37:25.1269888Z [INFO] Results:
2026-05-25T16:37:25.1270229Z [INFO] 
2026-05-25T16:37:25.1270599Z [ERROR] Failures: 
2026-05-25T16:37:25.1271218Z [ERROR]   TestShim.TestAll:41  had errors ==> expected: <0> but was: <681>
2026-05-25T16:37:25.1271736Z [INFO] 
2026-05-25T16:37:25.1271984Z [ERROR] Tests run: 657, Failures: 1, Errors: 0, Skipped: 23
2026-05-25T16:37:25.1272857Z [INFO] 
2026-05-25T16:37:25.1306907Z [INFO] ------------------------------------------------------------------------
2026-05-25T16:37:25.1307648Z [INFO] Reactor Summary for CLDR All Tools 49.0-SNAPSHOT:
2026-05-25T16:37:25.1308153Z [INFO] 
2026-05-25T16:37:25.1310842Z [INFO] CLDR All Tools ..................................... SUCCESS [  0.001 s]
2026-05-25T16:37:25.1311840Z [INFO] CLDR Code .......................................... FAILURE [21:15 min]
2026-05-25T16:37:25.1312899Z [INFO] CLDR RDF Tools ..................................... SKIPPED
2026-05-25T16:37:25.1313585Z [INFO] CLDR Survey Tool ................................... SKIPPED
2026-05-25T16:37:25.1314269Z [INFO] CLDR Keyboard Charts ............................... SKIPPED
2026-05-25T16:37:25.1314948Z [INFO] ------------------------------------------------------------------------
2026-05-25T16:37:25.1315528Z [INFO] BUILD FAILURE
2026-05-25T16:37:25.1316011Z [INFO] ------------------------------------------------------------------------
2026-05-25T16:37:25.1316598Z [INFO] Total time:  21:16 min
2026-05-25T16:37:25.1317015Z [INFO] Finished at: 2026-05-25T16:37:25Z
2026-05-25T16:37:25.1317574Z [INFO] ------------------------------------------------------------------------
2026-05-25T16:37:25.1322997Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.3.1:test (default-test) on project cldr-code: There are test failures.
2026-05-25T16:37:25.1324412Z [ERROR] 
2026-05-25T16:37:25.1325596Z [ERROR] Please refer to /home/runner/work/cldr/cldr/tools/cldr-code/target/surefire-reports for the individual test results.
2026-05-25T16:37:25.1327210Z [ERROR] Please refer to dump files (if any exist) [date].dump, [date]-jvmRun[N].dump and [date].dumpstream.
2026-05-25T16:37:25.1328531Z [ERROR] -> [Help 1]
2026-05-25T16:37:25.1329109Z [ERROR] 
2026-05-25T16:37:25.1329835Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-05-25T16:37:25.1330969Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-05-25T16:37:25.1331831Z [ERROR] 
2026-05-25T16:37:25.1333062Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-05-25T16:37:25.1334435Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
2026-05-25T16:37:25.1335371Z [ERROR] 
2026-05-25T16:37:25.1336110Z [ERROR] After correcting the problems, you can resume the build with the command
2026-05-25T16:37:25.1337073Z [ERROR]   mvn <args> -rf :cldr-code
2026-05-25T16:37:25.1542571Z ##[error]Process completed with exit code 1.
2026-05-25T16:37:25.1686428Z ##[group]Run test-summary/action@v2
2026-05-25T16:37:25.1686701Z with:
2026-05-25T16:37:25.1686935Z   paths: tools/*/target/surefire-reports/**/TEST-*.xml
2026-05-25T16:37:25.1687232Z env:
2026-05-25T16:37:25.1687407Z   CLDR_CHECK_MODE: BUILD
2026-05-25T16:37:25.1687739Z   JAVA_HOME: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/11.0.31-11/x64
2026-05-25T16:37:25.1688211Z   JAVA_HOME_11_X64: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/11.0.31-11/x64
2026-05-25T16:37:25.1688577Z ##[endgroup]
2026-05-25T16:37:25.6364669Z Post job cleanup.
2026-05-25T16:37:25.8186101Z Post job cleanup.
2026-05-25T16:37:25.9235065Z [command]/usr/bin/git version
2026-05-25T16:37:25.9278368Z git version 2.54.0
2026-05-25T16:37:25.9322018Z Temporarily overriding HOME='/home/runner/work/_temp/d9be752d-521a-42e0-8424-ea08cb744383' before making global git config changes
2026-05-25T16:37:25.9323720Z Adding repository directory to the temporary git global config as a safe directory
2026-05-25T16:37:25.9328402Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/cldr/cldr
2026-05-25T16:37:25.9362715Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-05-25T16:37:25.9395182Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-05-25T16:37:25.9671652Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-05-25T16:37:25.9697044Z http.https://github.com/.extraheader
2026-05-25T16:37:25.9709084Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-05-25T16:37:25.9738651Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-05-25T16:37:25.9964533Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-05-25T16:37:25.9993752Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-05-25T16:37:26.0344334Z Cleaning up orphan processes
2026-05-25T16:37:26.0688920Z ##[warning]Node.js 20 actions are deprecated. The following actions are running on Node.js 20 and may not work as expected: actions/cache@v4, actions/checkout@v4, actions/setup-java@v4. Actions will be forced to run with Node.js 24 by default starting June 2nd, 2026. Node.js 20 will be removed from the runner on September 16th, 2026. Please check if updated versions of these actions are available that support Node.js 24. To opt into Node.js 24 now, set the FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true environment variable on the runner or in your workflow file. Once Node.js 24 becomes the default, you can temporarily opt out by setting ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 38. `unicode-org__cldr__088667882207.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/unicode-org__cldr__088667882207.txt` (authoritative; read this, not the excerpt)
- **Repository**: `unicode-org/cldr`
- **Content hash (sha256, first 16)**: `5ee4c5dac98ddd68`
- **Body size**: 1,287,594 bytes, 13,225 lines
- **Excerpt**: final 120 of 13,225 lines, content-blind

```text
2026-07-21T15:10:39.4624643Z 	at org.junit.jupiter.engine.descriptor.TestMethodTestDescriptor.lambda$invokeTestMethod$7(TestMethodTestDescriptor.java:214)
2026-07-21T15:10:39.4626427Z 	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
2026-07-21T15:10:39.4628167Z 	at org.junit.jupiter.engine.descriptor.TestMethodTestDescriptor.invokeTestMethod(TestMethodTestDescriptor.java:210)
2026-07-21T15:10:39.4630576Z 	at org.junit.jupiter.engine.descriptor.TestMethodTestDescriptor.execute(TestMethodTestDescriptor.java:135)
2026-07-21T15:10:39.4632372Z 	at org.junit.jupiter.engine.descriptor.TestMethodTestDescriptor.execute(TestMethodTestDescriptor.java:66)
2026-07-21T15:10:39.4634105Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$6(NodeTestTask.java:151)
2026-07-21T15:10:39.4635999Z 	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
2026-07-21T15:10:39.4637773Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$8(NodeTestTask.java:141)
2026-07-21T15:10:39.4639940Z 	at org.junit.platform.engine.support.hierarchical.Node.around(Node.java:137)
2026-07-21T15:10:39.4641342Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$9(NodeTestTask.java:139)
2026-07-21T15:10:39.4643035Z 	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
2026-07-21T15:10:39.4644846Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.executeRecursively(NodeTestTask.java:138)
2026-07-21T15:10:39.4646548Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.execute(NodeTestTask.java:95)
2026-07-21T15:10:39.4647901Z 	at java.base/java.util.ArrayList.forEach(ArrayList.java:1596)
2026-07-21T15:10:39.4650133Z 	at org.junit.platform.engine.support.hierarchical.SameThreadHierarchicalTestExecutorService.invokeAll(SameThreadHierarchicalTestExecutorService.java:41)
2026-07-21T15:10:39.4652577Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$6(NodeTestTask.java:155)
2026-07-21T15:10:39.4654524Z 	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
2026-07-21T15:10:39.4656549Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$8(NodeTestTask.java:141)
2026-07-21T15:10:39.4658211Z 	at org.junit.platform.engine.support.hierarchical.Node.around(Node.java:137)
2026-07-21T15:10:39.4660060Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$9(NodeTestTask.java:139)
2026-07-21T15:10:39.4662053Z 	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
2026-07-21T15:10:39.4664338Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.executeRecursively(NodeTestTask.java:138)
2026-07-21T15:10:39.4665999Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.execute(NodeTestTask.java:95)
2026-07-21T15:10:39.4667338Z 	at java.base/java.util.ArrayList.forEach(ArrayList.java:1596)
2026-07-21T15:10:39.4669416Z 	at org.junit.platform.engine.support.hierarchical.SameThreadHierarchicalTestExecutorService.invokeAll(SameThreadHierarchicalTestExecutorService.java:41)
2026-07-21T15:10:39.4671791Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$6(NodeTestTask.java:155)
2026-07-21T15:10:39.4673576Z 	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
2026-07-21T15:10:39.4675337Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$8(NodeTestTask.java:141)
2026-07-21T15:10:39.4676860Z 	at org.junit.platform.engine.support.hierarchical.Node.around(Node.java:137)
2026-07-21T15:10:39.4678371Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$9(NodeTestTask.java:139)
2026-07-21T15:10:39.4680537Z 	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
2026-07-21T15:10:39.4682095Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.executeRecursively(NodeTestTask.java:138)
2026-07-21T15:10:39.4683517Z 	at org.junit.platform.engine.support.hierarchical.NodeTestTask.execute(NodeTestTask.java:95)
2026-07-21T15:10:39.4685744Z 	at org.junit.platform.engine.support.hierarchical.SameThreadHierarchicalTestExecutorService.submit(SameThreadHierarchicalTestExecutorService.java:35)
2026-07-21T15:10:39.4687838Z 	at org.junit.platform.engine.support.hierarchical.HierarchicalTestExecutor.execute(HierarchicalTestExecutor.java:57)
2026-07-21T15:10:39.4690077Z 	at org.junit.platform.engine.support.hierarchical.HierarchicalTestEngine.execute(HierarchicalTestEngine.java:54)
2026-07-21T15:10:39.4691742Z 	at org.junit.platform.launcher.core.EngineExecutionOrchestrator.execute(EngineExecutionOrchestrator.java:107)
2026-07-21T15:10:39.4693329Z 	at org.junit.platform.launcher.core.EngineExecutionOrchestrator.execute(EngineExecutionOrchestrator.java:88)
2026-07-21T15:10:39.4695224Z 	at org.junit.platform.launcher.core.EngineExecutionOrchestrator.lambda$execute$0(EngineExecutionOrchestrator.java:54)
2026-07-21T15:10:39.4697002Z 	at org.junit.platform.launcher.core.EngineExecutionOrchestrator.withInterceptedStreams(EngineExecutionOrchestrator.java:67)
2026-07-21T15:10:39.4698722Z 	at org.junit.platform.launcher.core.EngineExecutionOrchestrator.execute(EngineExecutionOrchestrator.java:52)
2026-07-21T15:10:39.4700336Z 	at org.junit.platform.launcher.core.DefaultLauncher.execute(DefaultLauncher.java:114)
2026-07-21T15:10:39.4701497Z 	at org.junit.platform.launcher.core.DefaultLauncher.execute(DefaultLauncher.java:86)
2026-07-21T15:10:39.4702882Z 	at org.junit.platform.launcher.core.DefaultLauncherSession$DelegatingLauncher.execute(DefaultLauncherSession.java:86)
2026-07-21T15:10:39.4704745Z 	at org.apache.maven.surefire.junitplatform.LazyLauncher.execute(LazyLauncher.java:56)
2026-07-21T15:10:39.4706185Z 	at org.apache.maven.surefire.junitplatform.JUnitPlatformProvider.execute(JUnitPlatformProvider.java:184)
2026-07-21T15:10:39.4707739Z 	at org.apache.maven.surefire.junitplatform.JUnitPlatformProvider.invokeAllTests(JUnitPlatformProvider.java:148)
2026-07-21T15:10:39.4710019Z 	at org.apache.maven.surefire.junitplatform.JUnitPlatformProvider.invoke(JUnitPlatformProvider.java:122)
2026-07-21T15:10:39.4711484Z 	at org.apache.maven.surefire.booter.ForkedBooter.runSuitesInProcess(ForkedBooter.java:385)
2026-07-21T15:10:39.4712679Z 	at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
2026-07-21T15:10:39.4713734Z 	at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
2026-07-21T15:10:39.4714727Z 	at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)
2026-07-21T15:10:39.4715324Z 
2026-07-21T15:10:39.7331617Z [INFO] 
2026-07-21T15:10:39.7332064Z [INFO] Results:
2026-07-21T15:10:39.7332443Z [INFO] 
2026-07-21T15:10:39.7332785Z [ERROR] Failures: 
2026-07-21T15:10:39.7333429Z [ERROR]   TestShim.TestAll:41  had errors ==> expected: <0> but was: <1654>
2026-07-21T15:10:39.7334177Z [INFO] 
2026-07-21T15:10:39.7334657Z [ERROR] Tests run: 670, Failures: 1, Errors: 0, Skipped: 23
2026-07-21T15:10:39.7335252Z [INFO] 
2026-07-21T15:10:39.7357721Z [INFO] ------------------------------------------------------------------------
2026-07-21T15:10:39.7358640Z [INFO] Reactor Summary for CLDR All Tools 49.0-SNAPSHOT:
2026-07-21T15:10:39.7368850Z [INFO] 
2026-07-21T15:10:39.7369973Z [INFO] CLDR All Tools ..................................... SUCCESS [  0.002 s]
2026-07-21T15:10:39.7371172Z [INFO] CLDR Code .......................................... FAILURE [22:48 min]
2026-07-21T15:10:39.7372233Z [INFO] CLDR RDF Tools ..................................... SKIPPED
2026-07-21T15:10:39.7373239Z [INFO] CLDR Survey Tool ................................... SKIPPED
2026-07-21T15:10:39.7416953Z [INFO] CLDR Keyboard Charts ............................... SKIPPED
2026-07-21T15:10:39.7418021Z [INFO] ------------------------------------------------------------------------
2026-07-21T15:10:39.7418924Z [INFO] BUILD FAILURE
2026-07-21T15:10:39.7420259Z [INFO] ------------------------------------------------------------------------
2026-07-21T15:10:39.7420976Z [INFO] Total time:  22:48 min
2026-07-21T15:10:39.7421365Z [INFO] Finished at: 2026-07-21T15:10:39Z
2026-07-21T15:10:39.7422373Z [INFO] ------------------------------------------------------------------------
2026-07-21T15:10:39.7424108Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.3.1:test (default-test) on project cldr-code: There are test failures.
2026-07-21T15:10:39.7436038Z [ERROR] 
2026-07-21T15:10:39.7436930Z [ERROR] Please refer to /home/runner/work/cldr/cldr/tools/cldr-code/target/surefire-reports for the individual test results.
2026-07-21T15:10:39.7437773Z [ERROR] Please refer to dump files (if any exist) [date].dump, [date]-jvmRun[N].dump and [date].dumpstream.
2026-07-21T15:10:39.7438528Z [ERROR] -> [Help 1]
2026-07-21T15:10:39.7438748Z [ERROR] 
2026-07-21T15:10:39.7439474Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-07-21T15:10:39.7440220Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-07-21T15:10:39.7440604Z [ERROR] 
2026-07-21T15:10:39.7441022Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-07-21T15:10:39.7441700Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
2026-07-21T15:10:39.7442132Z [ERROR] 
2026-07-21T15:10:39.7442472Z [ERROR] After correcting the problems, you can resume the build with the command
2026-07-21T15:10:39.7442892Z [ERROR]   mvn <args> -rf :cldr-code
2026-07-21T15:10:39.7600618Z ##[error]Process completed with exit code 1.
2026-07-21T15:10:39.7754272Z ##[group]Run test-summary/action@v2
2026-07-21T15:10:39.7754598Z with:
2026-07-21T15:10:39.7754867Z   paths: tools/*/target/surefire-reports/**/TEST-*.xml
2026-07-21T15:10:39.7755212Z env:
2026-07-21T15:10:39.7755404Z   CLDR_CHECK_MODE: BUILD
2026-07-21T15:10:39.7755640Z   JDK_VERSION: 21
2026-07-21T15:10:39.7755976Z   JAVA_HOME: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/21.0.11-10/x64
2026-07-21T15:10:39.7756511Z   JAVA_HOME_21_X64: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/21.0.11-10/x64
2026-07-21T15:10:39.7756915Z ##[endgroup]
2026-07-21T15:10:40.2587478Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-07-21T15:10:40.2588760Z Post job cleanup.
2026-07-21T15:10:40.3991342Z (node:5061) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-07-21T15:10:40.3992716Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-07-21T15:10:40.4166300Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-07-21T15:10:40.4167576Z Post job cleanup.
2026-07-21T15:10:40.5113183Z [command]/usr/bin/git version
2026-07-21T15:10:40.5155998Z git version 2.54.0
2026-07-21T15:10:40.5199310Z Temporarily overriding HOME='/home/runner/work/_temp/948e686d-be78-41dc-aa37-c08aedb8c219' before making global git config changes
2026-07-21T15:10:40.5200454Z Adding repository directory to the temporary git global config as a safe directory
2026-07-21T15:10:40.5205952Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/cldr/cldr
2026-07-21T15:10:40.5243736Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-07-21T15:10:40.5278745Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-07-21T15:10:40.5552246Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-21T15:10:40.5579930Z http.https://github.com/.extraheader
2026-07-21T15:10:40.5591353Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-07-21T15:10:40.5623624Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-07-21T15:10:40.5893237Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-21T15:10:40.5927226Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-07-21T15:10:40.6310448Z Cleaning up orphan processes
2026-07-21T15:10:40.6698769Z ##[warning]Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24: actions/cache@v4, actions/checkout@v4, actions/setup-java@v4. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 39. `webauthn4j__webauthn4j__084798963375.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/webauthn4j__webauthn4j__084798963375.txt` (authoritative; read this, not the excerpt)
- **Repository**: `webauthn4j/webauthn4j`
- **Content hash (sha256, first 16)**: `b0c3b21b6751bbb7`
- **Body size**: 404,419 bytes, 5,106 lines
- **Excerpt**: final 120 of 5,106 lines, content-blind

```text
2026-07-02T14:40:10.4532193Z   CODEQL_ACTION_VERSION: 4.36.3
2026-07-02T14:40:10.4532485Z   JOB_RUN_UUID: ca20874d-95bc-412e-9f04-989979ac31d2
2026-07-02T14:40:10.4532794Z   CODEQL_ACTION_INIT_HAS_RUN: true
2026-07-02T14:40:10.4533165Z   CODEQL_ACTION_ANALYSIS_KEY: .github/workflows/codeql-analysis.yml:analyze
2026-07-02T14:40:10.4533609Z   CODEQL_WORKFLOW_STARTED_AT: 2026-07-02T14:33:41.079Z
2026-07-02T14:40:10.4538520Z   CODEQL_ACTION_CLI_VERSION_INFO: {"cmd":"/opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/codeql","version":{"productName":"CodeQL","vendor":"GitHub","version":"2.25.6","sha":"7c492d06b1175b24bf72bfb8e0daba1bb3a21847","branches":["codeql-cli-2.25.6"],"copyright":"Copyright (C) 2019-2026 GitHub, Inc.","unpackedLocation":"/opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql","configFileLocation":"/home/runner/.config/codeql/config","configFileFound":false,"overlayVersion":4,"features":{"analysisSummaryV2Default":true,"buildModeOption":true,"bundleSupportsIncludeDiagnostics":true,"bundleSupportsIncludeLogs":true,"bundleSupportsOverlay":true,"databaseInterpretResultsSupportsSarifRunProperty":true,"featuresInVersionResult":true,"indirectTracingSupportsStaticBinaries":false,"informsAboutUnsupportedPathFilters":true,"supportsPython312":true,"mrvaPackCreate":true,"threatModelOption":true,"traceCommandUseBuildMode":true,"v2ramSizing":true,"mrvaPackCreateMultipleQueries":true,"setsCodeqlRunnerEnvVar":true,"sarifMergeRunsFromEqualCategory":true,"forceOverwrite":true,"generateSummarySymbolMap":true,"pythonDefaultIsToNotExtractStdlib":true,"queryServerRunQueries":true,"queryServerTrimCacheWithMode":true,"builtinExtractorsSpecifyDefaultQueries":true,"bqrsDiffResultSets":true,"bundleSupportsIncludeOption":true,"suppressesMissingFileBaselineWarning":true}}}
2026-07-02T14:40:10.4543723Z   CODEQL_RAM: 14579
2026-07-02T14:40:10.4543936Z   CODEQL_THREADS: 4
2026-07-02T14:40:10.4544239Z   CODEQL_SCRATCH_DIR: /home/runner/work/_temp/codeql_databases/working
2026-07-02T14:40:10.4544612Z   CODEQL_VERBOSITY: warnings
2026-07-02T14:40:10.4544912Z   CODEQL_DIST: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql
2026-07-02T14:40:10.4545245Z   CODEQL_PLATFORM: linux64
2026-07-02T14:40:10.4545492Z   CODEQL_PLATFORM_DLL_EXTENSION: .so
2026-07-02T14:40:10.4545888Z   CODEQL_JAVA_HOME: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/tools/linux64/java
2026-07-02T14:40:10.4546416Z   CODEQL_EXTRACTOR_JAVA_ROOT: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/java
2026-07-02T14:40:10.4546942Z   CODEQL_EXTRACTOR_JAVA_WIP_DATABASE: /home/runner/work/_temp/codeql_databases/java
2026-07-02T14:40:10.4547570Z   CODEQL_EXTRACTOR_JAVA_DIAGNOSTIC_DIR: /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java
2026-07-02T14:40:10.4548198Z   CODEQL_EXTRACTOR_JAVA_LOG_DIR: /home/runner/work/_temp/codeql_databases/java/log
2026-07-02T14:40:10.4548911Z   CODEQL_EXTRACTOR_JAVA_SCRATCH_DIR: /home/runner/work/_temp/codeql_databases/java/working
2026-07-02T14:40:10.4549498Z   CODEQL_EXTRACTOR_JAVA_TRAP_DIR: /home/runner/work/_temp/codeql_databases/java/trap/java
2026-07-02T14:40:10.4550076Z   CODEQL_EXTRACTOR_JAVA_SOURCE_ARCHIVE_DIR: /home/runner/work/_temp/codeql_databases/java/src
2026-07-02T14:40:10.4550520Z   CODEQL_EXTRACTOR_JAVA_THREADS: 4
2026-07-02T14:40:10.4550782Z   CODEQL_EXTRACTOR_JAVA_RAM: 14579
2026-07-02T14:40:10.4551165Z   CODEQL_TRACER_LOG: /home/runner/work/_temp/codeql_databases/log/build-tracer.log
2026-07-02T14:40:10.4551926Z   CODEQL_TRACER_DIAGNOSTICS_DIR: /home/runner/work/_temp/codeql_databases/diagnostic/tracer
2026-07-02T14:40:10.4552365Z   CODEQL_TRACER_LANGUAGES: java
2026-07-02T14:40:10.4552850Z   SEMMLE_PRELOAD_libtrace: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/tools/linux64/${LIB}_${PLATFORM}_trace.so
2026-07-02T14:40:10.4553564Z   SEMMLE_PRELOAD_libtrace32: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/tools/linux64/lib32trace.so
2026-07-02T14:40:10.4554227Z   SEMMLE_PRELOAD_libtrace64: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/tools/linux64/lib64trace.so
2026-07-02T14:40:10.4554953Z   CODEQL_RUNNER: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/tools/linux64/runner
2026-07-02T14:40:10.4555542Z   LD_PRELOAD: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/tools/linux64/${LIB}_${PLATFORM}_trace.so
2026-07-02T14:40:10.4555994Z ##[endgroup]
2026-07-02T14:40:10.9265156Z ##[error]Loaded a configuration file for version '4.36.3', but running version '4.36.2'
2026-07-02T14:40:11.1757664Z Post job cleanup.
2026-07-02T14:40:11.4238097Z ##[error]analyze post-action step failed: Loaded a configuration file for version '4.36.3', but running version '4.36.2'
2026-07-02T14:40:11.4408985Z Post job cleanup.
2026-07-02T14:40:12.3936769Z [command]/opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/codeql database export-diagnostics /home/runner/work/_temp/codeql_databases --db-cluster --format=sarif-latest --output=../codeql-failed-run.sarif --sarif-include-diagnostics -vvv
2026-07-02T14:40:12.9452970Z Writing logs to /home/runner/work/_temp/codeql_databases/log/database-export-diagnostics-20260702.144012.941.log.
2026-07-02T14:40:13.2087595Z Interpreting diagnostic messages...
2026-07-02T14:40:13.2102286Z Looking for diagnostics in /home/runner/work/_temp/codeql_databases/java/diagnostic...
2026-07-02T14:40:13.2109456Z Looking for diagnostics in /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors...
2026-07-02T14:40:13.2110485Z Looking for diagnostics in /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java...
2026-07-02T14:40:13.2111796Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--2939.jsonl.
2026-07-02T14:40:13.2374388Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--4101.jsonl.
2026-07-02T14:40:13.2425821Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3824.jsonl.
2026-07-02T14:40:13.2493651Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3025.jsonl.
2026-07-02T14:40:13.2550964Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5167.jsonl.
2026-07-02T14:40:13.2612976Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3306.jsonl.
2026-07-02T14:40:13.2665840Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--2883.jsonl.
2026-07-02T14:40:13.2753040Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--4032.jsonl.
2026-07-02T14:40:13.2773505Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3763.jsonl.
2026-07-02T14:40:13.2815330Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3145.jsonl.
2026-07-02T14:40:13.2851437Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3562.jsonl.
2026-07-02T14:40:13.2892793Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--2848.jsonl.
2026-07-02T14:40:13.2934865Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--2968.jsonl.
2026-07-02T14:40:13.2978687Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3424.jsonl.
2026-07-02T14:40:13.3017140Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3696.jsonl.
2026-07-02T14:40:13.3053839Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3278.jsonl.
2026-07-02T14:40:13.3086979Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--2998.jsonl.
2026-07-02T14:40:13.3117448Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5221.jsonl.
2026-07-02T14:40:13.3182941Z Looking for diagnostics in /home/runner/work/_temp/codeql_databases/java/diagnostic/codeql-action...
2026-07-02T14:40:13.3202601Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/codeql-action/codeql-action-2026-07-02T143345.494Z-0.json.
2026-07-02T14:40:13.3265595Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/codeql-action/codeql-action-2026-07-02T143347.654Z-2.json.
2026-07-02T14:40:13.3316710Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/codeql-action/codeql-action-2026-07-02T143346.478Z-1.json.
2026-07-02T14:40:13.3362246Z Looking for diagnostics in /home/runner/work/_temp/codeql_databases/diagnostic...
2026-07-02T14:40:13.3363807Z Looking for diagnostics in /home/runner/work/_temp/codeql_databases/diagnostic/tracer...
2026-07-02T14:40:13.3365667Z Found diagnostics file /home/runner/work/_temp/codeql_databases/diagnostic/cli-diagnostics-add-20260702T143352.817Z.json.
2026-07-02T14:40:13.3418668Z Found 4 raw diagnostic messages.
2026-07-02T14:40:13.3626820Z Processed diagnostic messages (removed 0 due to limits, created 0 summary diagnostics for status page).
2026-07-02T14:40:13.3658196Z Interpreted diagnostic messages (154ms).
2026-07-02T14:40:13.5114763Z Uploading failed SARIF file ../codeql-failed-run.sarif
2026-07-02T14:40:13.5116575Z Post-processing sarif files: ["../codeql-failed-run.sarif"]
2026-07-02T14:40:13.5128662Z Adding fingerprints to SARIF file. See https://docs.github.com/en/code-security/reference/code-scanning/sarif-support-for-code-scanning#data-for-preventing-duplicated-alerts for more information.
2026-07-02T14:40:13.5131752Z ##[group]Uploading code scanning results
2026-07-02T14:40:13.5409856Z Uploading results
2026-07-02T14:40:14.0490707Z Successfully uploaded results
2026-07-02T14:40:14.0491937Z ##[endgroup]
2026-07-02T14:40:14.0492678Z ##[group]Waiting for processing to finish
2026-07-02T14:40:19.1951028Z Analysis upload status is failed.
2026-07-02T14:40:19.1952888Z Successfully uploaded a SARIF file for the unsuccessful execution. Received expected "unsuccessful execution" processing error, and no other errors.
2026-07-02T14:40:19.1954922Z ##[endgroup]
2026-07-02T14:40:19.2078970Z CodeQL job status was configuration error.
2026-07-02T14:40:19.2193109Z Sending status report for init-post step.
2026-07-02T14:40:19.3818853Z Status report sent for init-post step.
2026-07-02T14:40:19.4035999Z Post job cleanup.
2026-07-02T14:40:19.5497236Z Post job cleanup.
2026-07-02T14:40:19.6368066Z [command]/usr/bin/git version
2026-07-02T14:40:19.6418869Z git version 2.54.0
2026-07-02T14:40:19.6464492Z Temporarily overriding HOME='/home/runner/work/_temp/c448bbaa-f6bc-4678-a7a3-3f5ab85c8484' before making global git config changes
2026-07-02T14:40:19.6465485Z Adding repository directory to the temporary git global config as a safe directory
2026-07-02T14:40:19.6471248Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/webauthn4j/webauthn4j
2026-07-02T14:40:19.6516596Z Removing SSH command configuration
2026-07-02T14:40:19.6522880Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-07-02T14:40:19.6569003Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-07-02T14:40:19.6961317Z Removing HTTP extra header
2026-07-02T14:40:19.6967876Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-02T14:40:19.7015941Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-07-02T14:40:19.7406981Z Removing includeIf entries pointing to credentials config files
2026-07-02T14:40:19.7413944Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-02T14:40:19.7449920Z includeif.gitdir:/home/runner/work/webauthn4j/webauthn4j/.git.path
2026-07-02T14:40:19.7450757Z includeif.gitdir:/home/runner/work/webauthn4j/webauthn4j/.git/worktrees/*.path
2026-07-02T14:40:19.7451228Z includeif.gitdir:/github/workspace/.git.path
2026-07-02T14:40:19.7451864Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-02T14:40:19.7459471Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/webauthn4j/webauthn4j/.git.path
2026-07-02T14:40:19.7492930Z /home/runner/work/_temp/git-credentials-b32b6e72-2325-4bbb-b403-2675c650e64c.config
2026-07-02T14:40:19.7503971Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/webauthn4j/webauthn4j/.git.path /home/runner/work/_temp/git-credentials-b32b6e72-2325-4bbb-b403-2675c650e64c.config
2026-07-02T14:40:19.7549750Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/webauthn4j/webauthn4j/.git/worktrees/*.path
2026-07-02T14:40:19.7582291Z /home/runner/work/_temp/git-credentials-b32b6e72-2325-4bbb-b403-2675c650e64c.config
2026-07-02T14:40:19.7591360Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/webauthn4j/webauthn4j/.git/worktrees/*.path /home/runner/work/_temp/git-credentials-b32b6e72-2325-4bbb-b403-2675c650e64c.config
2026-07-02T14:40:19.7634182Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-07-02T14:40:19.7666095Z /github/runner_temp/git-credentials-b32b6e72-2325-4bbb-b403-2675c650e64c.config
2026-07-02T14:40:19.7673785Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git.path /github/runner_temp/git-credentials-b32b6e72-2325-4bbb-b403-2675c650e64c.config
2026-07-02T14:40:19.7715484Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-02T14:40:19.7746715Z /github/runner_temp/git-credentials-b32b6e72-2325-4bbb-b403-2675c650e64c.config
2026-07-02T14:40:19.7756165Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path /github/runner_temp/git-credentials-b32b6e72-2325-4bbb-b403-2675c650e64c.config
2026-07-02T14:40:19.7798321Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-07-02T14:40:19.8186889Z Removing credentials config '/home/runner/work/_temp/git-credentials-b32b6e72-2325-4bbb-b403-2675c650e64c.config'
2026-07-02T14:40:19.8340456Z Cleaning up orphan processes
2026-07-02T14:40:19.8663620Z Terminate orphan process: pid (2625) (java)
2026-07-02T14:40:19.8703789Z Terminate orphan process: pid (2688) (java)
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---

## 40. `webauthn4j__webauthn4j__085896676258.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/webauthn4j__webauthn4j__085896676258.txt` (authoritative; read this, not the excerpt)
- **Repository**: `webauthn4j/webauthn4j`
- **Content hash (sha256, first 16)**: `f97b490898943314`
- **Body size**: 405,648 bytes, 5,124 lines
- **Excerpt**: final 120 of 5,124 lines, content-blind

```text
2026-07-08T14:41:08.3655979Z   CODEQL_ACTION_VERSION: 4.36.3
2026-07-08T14:41:08.3656247Z   JOB_RUN_UUID: ceed4082-e63c-4194-9c0d-1ad4ee37ec76
2026-07-08T14:41:08.3656547Z   CODEQL_ACTION_INIT_HAS_RUN: true
2026-07-08T14:41:08.3656897Z   CODEQL_ACTION_ANALYSIS_KEY: .github/workflows/codeql-analysis.yml:analyze
2026-07-08T14:41:08.3657309Z   CODEQL_WORKFLOW_STARTED_AT: 2026-07-08T14:35:06.160Z
2026-07-08T14:41:08.3661915Z   CODEQL_ACTION_CLI_VERSION_INFO: {"cmd":"/opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/codeql","version":{"productName":"CodeQL","vendor":"GitHub","version":"2.25.6","sha":"7c492d06b1175b24bf72bfb8e0daba1bb3a21847","branches":["codeql-cli-2.25.6"],"copyright":"Copyright (C) 2019-2026 GitHub, Inc.","unpackedLocation":"/opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql","configFileLocation":"/home/runner/.config/codeql/config","configFileFound":false,"overlayVersion":4,"features":{"analysisSummaryV2Default":true,"buildModeOption":true,"bundleSupportsIncludeDiagnostics":true,"bundleSupportsIncludeLogs":true,"bundleSupportsOverlay":true,"databaseInterpretResultsSupportsSarifRunProperty":true,"featuresInVersionResult":true,"indirectTracingSupportsStaticBinaries":false,"informsAboutUnsupportedPathFilters":true,"supportsPython312":true,"mrvaPackCreate":true,"threatModelOption":true,"traceCommandUseBuildMode":true,"v2ramSizing":true,"mrvaPackCreateMultipleQueries":true,"setsCodeqlRunnerEnvVar":true,"sarifMergeRunsFromEqualCategory":true,"forceOverwrite":true,"generateSummarySymbolMap":true,"pythonDefaultIsToNotExtractStdlib":true,"queryServerRunQueries":true,"queryServerTrimCacheWithMode":true,"builtinExtractorsSpecifyDefaultQueries":true,"bqrsDiffResultSets":true,"bundleSupportsIncludeOption":true,"suppressesMissingFileBaselineWarning":true}}}
2026-07-08T14:41:08.3666624Z   CODEQL_RAM: 14574
2026-07-08T14:41:08.3666820Z   CODEQL_THREADS: 4
2026-07-08T14:41:08.3667099Z   CODEQL_SCRATCH_DIR: /home/runner/work/_temp/codeql_databases/working
2026-07-08T14:41:08.3667434Z   CODEQL_VERBOSITY: warnings
2026-07-08T14:41:08.3667712Z   CODEQL_DIST: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql
2026-07-08T14:41:08.3668020Z   CODEQL_PLATFORM: linux64
2026-07-08T14:41:08.3668245Z   CODEQL_PLATFORM_DLL_EXTENSION: .so
2026-07-08T14:41:08.3668600Z   CODEQL_JAVA_HOME: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/tools/linux64/java
2026-07-08T14:41:08.3669079Z   CODEQL_EXTRACTOR_JAVA_ROOT: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/java
2026-07-08T14:41:08.3669552Z   CODEQL_EXTRACTOR_JAVA_WIP_DATABASE: /home/runner/work/_temp/codeql_databases/java
2026-07-08T14:41:08.3670120Z   CODEQL_EXTRACTOR_JAVA_DIAGNOSTIC_DIR: /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java
2026-07-08T14:41:08.3670689Z   CODEQL_EXTRACTOR_JAVA_LOG_DIR: /home/runner/work/_temp/codeql_databases/java/log
2026-07-08T14:41:08.3671601Z   CODEQL_EXTRACTOR_JAVA_SCRATCH_DIR: /home/runner/work/_temp/codeql_databases/java/working
2026-07-08T14:41:08.3672125Z   CODEQL_EXTRACTOR_JAVA_TRAP_DIR: /home/runner/work/_temp/codeql_databases/java/trap/java
2026-07-08T14:41:08.3672662Z   CODEQL_EXTRACTOR_JAVA_SOURCE_ARCHIVE_DIR: /home/runner/work/_temp/codeql_databases/java/src
2026-07-08T14:41:08.3673066Z   CODEQL_EXTRACTOR_JAVA_THREADS: 4
2026-07-08T14:41:08.3673319Z   CODEQL_EXTRACTOR_JAVA_RAM: 14574
2026-07-08T14:41:08.3673671Z   CODEQL_TRACER_LOG: /home/runner/work/_temp/codeql_databases/log/build-tracer.log
2026-07-08T14:41:08.3674174Z   CODEQL_TRACER_DIAGNOSTICS_DIR: /home/runner/work/_temp/codeql_databases/diagnostic/tracer
2026-07-08T14:41:08.3674576Z   CODEQL_TRACER_LANGUAGES: java
2026-07-08T14:41:08.3675022Z   SEMMLE_PRELOAD_libtrace: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/tools/linux64/${LIB}_${PLATFORM}_trace.so
2026-07-08T14:41:08.3675667Z   SEMMLE_PRELOAD_libtrace32: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/tools/linux64/lib32trace.so
2026-07-08T14:41:08.3676277Z   SEMMLE_PRELOAD_libtrace64: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/tools/linux64/lib64trace.so
2026-07-08T14:41:08.3676821Z   CODEQL_RUNNER: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/tools/linux64/runner
2026-07-08T14:41:08.3677359Z   LD_PRELOAD: /opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/tools/linux64/${LIB}_${PLATFORM}_trace.so
2026-07-08T14:41:08.3677772Z ##[endgroup]
2026-07-08T14:41:08.9321594Z ##[error]Loaded a configuration file for version '4.36.3', but running version '4.37.0'
2026-07-08T14:41:09.1443883Z Post job cleanup.
2026-07-08T14:41:09.3710239Z ##[error]analyze post-action step failed: Loaded a configuration file for version '4.36.3', but running version '4.37.0'
2026-07-08T14:41:09.3855414Z Post job cleanup.
2026-07-08T14:41:10.0327203Z [command]/opt/hostedtoolcache/CodeQL/2.25.6/x64/codeql/codeql database export-diagnostics /home/runner/work/_temp/codeql_databases --db-cluster --format=sarif-latest --output=../codeql-failed-run.sarif --sarif-include-diagnostics -vvv
2026-07-08T14:41:10.6463084Z Writing logs to /home/runner/work/_temp/codeql_databases/log/database-export-diagnostics-20260708.144110.642.log.
2026-07-08T14:41:10.9028270Z Interpreting diagnostic messages...
2026-07-08T14:41:10.9042976Z Looking for diagnostics in /home/runner/work/_temp/codeql_databases/java/diagnostic...
2026-07-08T14:41:10.9046069Z Looking for diagnostics in /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors...
2026-07-08T14:41:10.9050432Z Looking for diagnostics in /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java...
2026-07-08T14:41:10.9052181Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3111.jsonl.
2026-07-08T14:41:10.9332610Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--2846.jsonl.
2026-07-08T14:41:10.9379775Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3702.jsonl.
2026-07-08T14:41:10.9439496Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3274.jsonl.
2026-07-08T14:41:10.9497705Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--2989.jsonl.
2026-07-08T14:41:10.9562314Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--2959.jsonl.
2026-07-08T14:41:10.9602934Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--2810.jsonl.
2026-07-08T14:41:10.9648116Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--2902.jsonl.
2026-07-08T14:41:10.9688877Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--4131.jsonl.
2026-07-08T14:41:10.9720288Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3246.jsonl.
2026-07-08T14:41:10.9749424Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5134.jsonl.
2026-07-08T14:41:10.9786110Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3509.jsonl.
2026-07-08T14:41:10.9831020Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3391.jsonl.
2026-07-08T14:41:10.9873684Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--5189.jsonl.
2026-07-08T14:41:10.9903953Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3764.jsonl.
2026-07-08T14:41:10.9934806Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--4038.jsonl.
2026-07-08T14:41:10.9963113Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--2930.jsonl.
2026-07-08T14:41:10.9990130Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/extractors/java/java-extractor--3638.jsonl.
2026-07-08T14:41:11.0082256Z Looking for diagnostics in /home/runner/work/_temp/codeql_databases/java/diagnostic/codeql-action...
2026-07-08T14:41:11.0092483Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/codeql-action/codeql-action-2026-07-08T143516.460Z-2.json.
2026-07-08T14:41:11.0145047Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/codeql-action/codeql-action-2026-07-08T143514.250Z-0.json.
2026-07-08T14:41:11.0192487Z Found diagnostics file /home/runner/work/_temp/codeql_databases/java/diagnostic/codeql-action/codeql-action-2026-07-08T143515.229Z-1.json.
2026-07-08T14:41:11.0220302Z Looking for diagnostics in /home/runner/work/_temp/codeql_databases/diagnostic...
2026-07-08T14:41:11.0221625Z Looking for diagnostics in /home/runner/work/_temp/codeql_databases/diagnostic/tracer...
2026-07-08T14:41:11.0222978Z Found diagnostics file /home/runner/work/_temp/codeql_databases/diagnostic/cli-diagnostics-add-20260708T143521.629Z.json.
2026-07-08T14:41:11.0281963Z Found 4 raw diagnostic messages.
2026-07-08T14:41:11.0511329Z Processed diagnostic messages (removed 0 due to limits, created 0 summary diagnostics for status page).
2026-07-08T14:41:11.0533297Z Interpreted diagnostic messages (148ms).
2026-07-08T14:41:11.1840535Z Uploading failed SARIF file ../codeql-failed-run.sarif
2026-07-08T14:41:11.1842379Z Post-processing sarif files: ["../codeql-failed-run.sarif"]
2026-07-08T14:41:11.1852014Z Adding fingerprints to SARIF file. See https://docs.github.com/en/code-security/reference/code-scanning/sarif-support-for-code-scanning#data-for-preventing-duplicated-alerts for more information.
2026-07-08T14:41:11.1854540Z ##[group]Uploading code scanning results
2026-07-08T14:41:11.2102203Z Uploading results
2026-07-08T14:41:11.8149828Z Successfully uploaded results
2026-07-08T14:41:11.8150349Z ##[endgroup]
2026-07-08T14:41:11.8151954Z ##[group]Waiting for processing to finish
2026-07-08T14:41:17.0442208Z Analysis upload status is failed.
2026-07-08T14:41:17.0443492Z Successfully uploaded a SARIF file for the unsuccessful execution. Received expected "unsuccessful execution" processing error, and no other errors.
2026-07-08T14:41:17.0444489Z ##[endgroup]
2026-07-08T14:41:17.0553765Z CodeQL job status was configuration error.
2026-07-08T14:41:17.0650494Z Sending status report for init-post step.
2026-07-08T14:41:17.2711059Z Status report sent for init-post step.
2026-07-08T14:41:17.2848945Z Post job cleanup.
2026-07-08T14:41:17.4162976Z Post job cleanup.
2026-07-08T14:41:17.5056699Z [command]/usr/bin/git version
2026-07-08T14:41:17.5133933Z git version 2.54.0
2026-07-08T14:41:17.5179948Z Temporarily overriding HOME='/home/runner/work/_temp/bc9ff508-c088-4d8e-b735-d58acee1761f' before making global git config changes
2026-07-08T14:41:17.5181682Z Adding repository directory to the temporary git global config as a safe directory
2026-07-08T14:41:17.5190578Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/webauthn4j/webauthn4j
2026-07-08T14:41:17.5240668Z Removing SSH command configuration
2026-07-08T14:41:17.5249561Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-07-08T14:41:17.5310061Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-07-08T14:41:17.5738750Z Removing HTTP extra header
2026-07-08T14:41:17.5745627Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-07-08T14:41:17.5788661Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-07-08T14:41:17.6131490Z Removing includeIf entries pointing to credentials config files
2026-07-08T14:41:17.6138651Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-07-08T14:41:17.6171886Z includeif.gitdir:/home/runner/work/webauthn4j/webauthn4j/.git.path
2026-07-08T14:41:17.6172982Z includeif.gitdir:/home/runner/work/webauthn4j/webauthn4j/.git/worktrees/*.path
2026-07-08T14:41:17.6173819Z includeif.gitdir:/github/workspace/.git.path
2026-07-08T14:41:17.6174473Z includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-08T14:41:17.6182195Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/webauthn4j/webauthn4j/.git.path
2026-07-08T14:41:17.6213602Z /home/runner/work/_temp/git-credentials-4afd9420-aabe-4ba3-8ae7-e6b59865c35f.config
2026-07-08T14:41:17.6223022Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/webauthn4j/webauthn4j/.git.path /home/runner/work/_temp/git-credentials-4afd9420-aabe-4ba3-8ae7-e6b59865c35f.config
2026-07-08T14:41:17.6277724Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/home/runner/work/webauthn4j/webauthn4j/.git/worktrees/*.path
2026-07-08T14:41:17.6310010Z /home/runner/work/_temp/git-credentials-4afd9420-aabe-4ba3-8ae7-e6b59865c35f.config
2026-07-08T14:41:17.6320046Z [command]/usr/bin/git config --local --unset includeif.gitdir:/home/runner/work/webauthn4j/webauthn4j/.git/worktrees/*.path /home/runner/work/_temp/git-credentials-4afd9420-aabe-4ba3-8ae7-e6b59865c35f.config
2026-07-08T14:41:17.6360304Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git.path
2026-07-08T14:41:17.6388036Z /github/runner_temp/git-credentials-4afd9420-aabe-4ba3-8ae7-e6b59865c35f.config
2026-07-08T14:41:17.6395534Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git.path /github/runner_temp/git-credentials-4afd9420-aabe-4ba3-8ae7-e6b59865c35f.config
2026-07-08T14:41:17.6433122Z [command]/usr/bin/git config --local --get-all includeif.gitdir:/github/workspace/.git/worktrees/*.path
2026-07-08T14:41:17.6460751Z /github/runner_temp/git-credentials-4afd9420-aabe-4ba3-8ae7-e6b59865c35f.config
2026-07-08T14:41:17.6468466Z [command]/usr/bin/git config --local --unset includeif.gitdir:/github/workspace/.git/worktrees/*.path /github/runner_temp/git-credentials-4afd9420-aabe-4ba3-8ae7-e6b59865c35f.config
2026-07-08T14:41:17.6506188Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-07-08T14:41:17.6822956Z Removing credentials config '/home/runner/work/_temp/git-credentials-4afd9420-aabe-4ba3-8ae7-e6b59865c35f.config'
2026-07-08T14:41:17.6949701Z Cleaning up orphan processes
2026-07-08T14:41:17.7202666Z Terminate orphan process: pid (2572) (java)
2026-07-08T14:41:17.7234356Z Terminate orphan process: pid (2636) (java)
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---
