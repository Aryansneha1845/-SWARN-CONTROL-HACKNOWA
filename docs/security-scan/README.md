# ZAP baseline scan — proof artifact for the Digital Safety track

Goal: an OWASP ZAP baseline HTML report against the HackNowa live URLs,
committed here as `zap_baseline.html`. Takes ~15 min, free, Windows-native.

## 1. Install (once)
1. Download OWASP ZAP Windows installer: https://www.zaproxy.org/download/
2. Install with defaults (bundles Java — nothing else needed).

## 2. Run baseline (after Render + Vercel deploys are live)
1. Open ZAP Desktop → **Automated Scan** → enter the Vercel URL
   (`https://<your-app>.vercel.app`) → Scan.
2. Repeat for the backend health endpoint
   (`https://<your-svc>.onrender.com/health`).
3. Menu **Report → Generate Report → HTML** → save each as
   `docs/security-scan/zap_baseline_frontend.html` /
   `zap_baseline_backend.html` in this repo.

## 3. What the jury wants to see
- No HIGH/CRITICAL findings on our own code (Render/Vercel infra warnings
  are the host's, not ours — note that in the submission description).
- Security headers present (nosniff, DENY framing, CSP) — all set server-side.
- `/docs` 404 on the Render backend (prod-locked API).

## 4. If findings appear
- Fix in code (usually a header or CORS tweak), redeploy, re-scan.
- Commit the final clean report — judges check the date on it.
