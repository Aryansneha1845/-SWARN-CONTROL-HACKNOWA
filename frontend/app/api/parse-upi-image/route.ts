/* Same-origin proxy for screenshot upload: browser -> Next.js server -> FastAPI.
   Forwards the multipart body untouched (2 MB cap) with the server-side key. */
const BACKEND = process.env.BACKEND_URL || 'http://localhost:8000';
const KEY = process.env.SWARN_API_KEY || '';
const MAX_UPLOAD = 2 * 1024 * 1024 + 16 * 1024;

export async function POST(req: Request) {
  const ctype = req.headers.get('content-type') || '';
  if (!ctype.startsWith('multipart/form-data')) {
    return Response.json({ detail: 'multipart upload required' }, { status: 400 });
  }
  const buf = await req.arrayBuffer();
  if (buf.byteLength > MAX_UPLOAD) {
    return Response.json({ detail: 'Screenshot too large (2 MB max)' }, { status: 413 });
  }
  const r = await fetch(`${BACKEND}/parse-upi-image`, {
    method: 'POST',
    headers: { 'Content-Type': ctype, ...(KEY ? { 'X-API-Key': KEY } : {}) },
    body: buf,
  });
  const data = await r.json().catch(() => ({ detail: 'Upstream error' }));
  return Response.json(data, { status: r.status });
}
