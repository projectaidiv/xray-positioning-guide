import * as THREE from '/node_modules/three/build/three.module.js';

const W = 1100, H = 700, D = Math.PI / 180;
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
document.body.style.margin = 0;
document.body.appendChild(renderer.domElement);

const V = (x, y, z) => new THREE.Vector3(x, y, z);
const skin = new THREE.MeshStandardMaterial({ color: 0xdfe7f0, roughness: 0.55 });
const metalDark = new THREE.MeshStandardMaterial({ color: 0x2b3a4c, roughness: 0.4, metalness: 0.5 });
const metalLight = new THREE.MeshStandardMaterial({ color: 0xaebccb, roughness: 0.35, metalness: 0.6 });
const detMat = new THREE.MeshStandardMaterial({ color: 0x172433, roughness: 0.35, metalness: 0.4 });
const detFace = new THREE.MeshStandardMaterial({ color: 0x7e93a9, roughness: 0.3, metalness: 0.3 });
const padMat = new THREE.MeshStandardMaterial({ color: 0x7fb0c9, roughness: 0.7 });
const woodMat = new THREE.MeshStandardMaterial({ color: 0xb9c4cf, roughness: 0.6 });

function mesh(geo, mat, pos, parent, shadow = true) {
  const m = new THREE.Mesh(geo, mat);
  if (pos) m.position.set(...pos);
  m.castShadow = shadow; m.receiveShadow = true;
  if (parent) parent.add(m);
  return m;
}
function grp(parent, pos = [0, 0, 0], rot = [0, 0, 0]) {
  const g = new THREE.Group();
  g.position.set(...pos);
  g.rotation.set(rot[0] * D, rot[1] * D, rot[2] * D, 'XYZ');
  parent.add(g);
  return g;
}
function bone(g, r, L) {
  const cap = mesh(new THREE.CapsuleGeometry(r, Math.max(L - 2 * r, 0.001), 8, 24), skin, [0, -L / 2, 0], g);
  return cap;
}
const mir = (r) => [r[0], -r[1], -r[2]];

// ------------------------------------------------------------ mannequin
// الجسم بيبص ناحية +Z، والمركز عند الحوض. side L = ناحية +X (شمال المريض)
function Body(p = {}) {
  const root = new THREE.Group();
  const z3 = [0, 0, 0];
  const ell = (rx, ry, rz, pos, parent) => {
    const m = mesh(new THREE.SphereGeometry(1, 32, 24), skin, pos, parent);
    m.scale.set(rx, ry, rz); return m;
  };
  ell(0.17, 0.11, 0.115, [0, 0, 0], root);
  const torso = grp(root, [0, 0.05, 0], p.torso || z3);
  ell(0.15, 0.14, 0.10, [0, 0.10, 0], torso);
  ell(0.185, 0.2, 0.115, [0, 0.31, 0], torso);
  mesh(new THREE.CylinderGeometry(0.048, 0.055, 0.12, 20), skin, [0, 0.52, 0], torso);
  const head = grp(torso, [0, 0.58, 0], p.head || z3);
  ell(0.098, 0.12, 0.108, [0, 0.10, 0], head);
  const nose = mesh(new THREE.ConeGeometry(0.02, 0.045, 16), skin, [0, 0.09, 0.115], head);
  nose.rotation.x = 90 * D;

  const arm = (sx, sh, el, wr) => {
    const m = sx > 0 ? (r) => r : mir;
    const gs = grp(torso, [sx * 0.215, 0.44, 0], m(sh || z3));
    mesh(new THREE.SphereGeometry(0.056, 24, 16), skin, [0, 0, 0], gs);
    bone(gs, 0.045, 0.30);
    const ge = grp(gs, [0, -0.30, 0], m(el || z3));
    mesh(new THREE.SphereGeometry(0.04, 20, 14), skin, [0, 0, 0], ge);
    bone(ge, 0.037, 0.26);
    const gw = grp(ge, [0, -0.26, 0], m(wr || z3));
    const hand = mesh(new THREE.CapsuleGeometry(0.04, 0.10, 8, 16), skin, [0, -0.085, 0], gw);
    hand.scale.set(0.42, 1, 1);
  };
  arm(+1, p.lSh, p.lEl, p.lWr);
  arm(-1, p.rSh, p.rEl, p.rWr);

  const leg = (sx, hip, kn, an) => {
    const m = sx > 0 ? (r) => r : mir;
    const gh = grp(root, [sx * 0.09, -0.03, 0], m(hip || z3));
    mesh(new THREE.SphereGeometry(0.078, 24, 16), skin, [0, 0, 0], gh);
    bone(gh, 0.075, 0.44);
    const gk = grp(gh, [0, -0.44, 0], m(kn || z3));
    mesh(new THREE.SphereGeometry(0.058, 20, 14), skin, [0, 0, 0], gk);
    bone(gk, 0.055, 0.43);
    const ga = grp(gk, [0, -0.43, 0], m(an || z3));
    const foot = mesh(new THREE.BoxGeometry(0.09, 0.055, 0.25), skin, [0, -0.03, 0.07], ga);
    foot.geometry.translate(0, 0, 0);
  };
  leg(+1, p.lHip, p.lKn, p.lAn);
  leg(-1, p.rHip, p.rKn, p.rAn);
  return root;
}

// ------------------------------------------------------------ equipment
function tube(scene, pos, target) {
  const g = new THREE.Group();
  g.position.copy(pos);
  mesh(new THREE.BoxGeometry(0.30, 0.22, 0.40), metalDark, [0, 0.0, 0], g);
  mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.34, 24), metalLight, [0, 0.02, 0], g).rotation.z = 90 * D;
  mesh(new THREE.BoxGeometry(0.22, 0.12, 0.22), metalLight, [0, -0.17, 0], g);
  mesh(new THREE.BoxGeometry(0.16, 0.02, 0.16), new THREE.MeshBasicMaterial({ color: 0xffd27a }), [0, -0.235, 0], g, false);
  g.quaternion.setFromUnitVectors(V(0, -1, 0), target.clone().sub(pos).normalize());
  scene.add(g);
  // عمود التعليق في السقف
  const top = 3.1, h = top - pos.y;
  mesh(new THREE.CylinderGeometry(0.03, 0.03, h, 16), metalLight, [pos.x, pos.y + h / 2, pos.z], scene);
  mesh(new THREE.BoxGeometry(0.4, 0.06, 0.3), metalDark, [pos.x, top, pos.z], scene);
}
function beam(scene, pos, cr, end, field) {
  const dir = pos.clone().sub(end);
  const L = dir.length();
  const geo = new THREE.CylinderGeometry(0.004, 1, 1, 4, 1, true);
  geo.rotateY(45 * D);
  const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: 0xffa81c, transparent: true, opacity: 0.2, side: THREE.DoubleSide, depthWrite: false }));
  m.scale.set(field / 1.414, L, field / 1.414);
  m.position.copy(pos.clone().add(end).multiplyScalar(0.5));
  m.quaternion.setFromUnitVectors(V(0, 1, 0), dir.clone().normalize());
  scene.add(m);
  m.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: 0xff9f0a })));
  // الشعاع المركزي (CR)
  const cl = pos.clone().sub(end).length();
  const ray = new THREE.Mesh(new THREE.CylinderGeometry(0.0045, 0.0045, cl, 8), new THREE.MeshBasicMaterial({ color: 0xff2d2d }));
  ray.position.copy(pos.clone().add(end).multiplyScalar(0.5));
  ray.quaternion.setFromUnitVectors(V(0, 1, 0), dir.clone().normalize());
  scene.add(ray);
  const dot = new THREE.Mesh(new THREE.SphereGeometry(0.017, 16, 12), new THREE.MeshBasicMaterial({ color: 0xff2d2d }));
  dot.position.copy(cr); scene.add(dot);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.03, 0.004, 8, 32), new THREE.MeshBasicMaterial({ color: 0xffffff }));
  ring.position.copy(cr); ring.quaternion.setFromUnitVectors(V(0, 0, 1), dir.clone().normalize()); scene.add(ring);
}
function uprightDetector(scene, x, y, z = 0, size = [0.46, 0.58]) {
  const g = new THREE.Group(); g.position.set(x, y, z); scene.add(g);
  mesh(new THREE.BoxGeometry(0.06, size[1] + 0.06, size[0] + 0.06), detMat, [0.0, 0, 0], g);
  mesh(new THREE.BoxGeometry(0.01, size[1] - 0.02, size[0] - 0.02), detFace, [-0.031, 0, 0], g);
  mesh(new THREE.BoxGeometry(0.08, 2.1, 0.1), metalLight, [0.08, 0.95 - y + 0.05, 0], g);
  mesh(new THREE.BoxGeometry(0.5, 0.05, 0.6), metalDark, [0.08, -y + 0.025, 0], g);
}
function room(scene) {
  scene.background = new THREE.Color(0xe9eff5);
  scene.fog = new THREE.Fog(0xe9eff5, 7, 20);
  const floor = new THREE.Mesh(new THREE.CircleGeometry(40, 64), new THREE.MeshStandardMaterial({ color: 0xe3eaf1, roughness: 0.9 }));
  floor.rotation.x = -90 * D; floor.receiveShadow = true; scene.add(floor);
  scene.add(new THREE.HemisphereLight(0xffffff, 0xb8c6d4, 0.85));
  const sun = new THREE.DirectionalLight(0xffffff, 1.7);
  sun.position.set(2.5, 5, 4); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -4, right: 4, top: 4, bottom: -4, near: 0.5, far: 14 });
  sun.shadow.bias = -0.0004; sun.shadow.radius = 4;
  scene.add(sun);
}
function table(scene, glass) {
  const top = new THREE.Mesh(new THREE.BoxGeometry(2.15, 0.05, 0.62),
    new THREE.MeshPhysicalMaterial({ color: 0xcfd9e3, transparent: glass, opacity: glass ? 0.4 : 1, roughness: 0.3 }));
  top.position.set(-0.07, 0.855, 0); top.receiveShadow = true; top.castShadow = true; scene.add(top);
  mesh(new THREE.BoxGeometry(2.0, 0.03, 0.55), padMat, [-0.07, 0.895, 0], scene);
  mesh(new THREE.BoxGeometry(0.5, 0.78, 0.4), metalLight, [-0.07, 0.4, 0], scene);
  mesh(new THREE.BoxGeometry(1.1, 0.04, 0.7), metalDark, [-0.07, 0.02, 0], scene);
}
function flatDetector(scene, x, y, z, sx = 0.30, sz = 0.40) {
  mesh(new THREE.BoxGeometry(sx, 0.022, sz), detMat, [x, y, z], scene);
  mesh(new THREE.BoxGeometry(sx - 0.03, 0.004, sz - 0.03), detFace, [x, y + 0.012, z], scene, false);
}

// ------------------------------------------------------------ scenes
const FRONT = 0.155;       // وجه الديتكتور القائم (x)
function standing(cfg) {
  const scene = new THREE.Scene(); room(scene);
  const det = cfg.detY, ty = cfg.crY;
  uprightDetector(scene, FRONT + 0.03, det);
  const body = Body(cfg.pose);
  const holder = grp(scene, [cfg.px, 0.95, 0], [0, cfg.ry || 0, 0]);
  holder.add(body);
  const tp = V(FRONT - cfg.sid, ty, 0);
  const crp = V(cfg.crx ?? 0.0, ty, 0);
  tube(scene, tp, V(FRONT, ty, 0));
  beam(scene, tp, crp, V(FRONT, ty, 0), cfg.field);
  return scene;
}
function lying(cfg) {
  const scene = new THREE.Scene(); room(scene);
  table(scene, true);
  const P = grp(scene, [cfg.xr, cfg.yr || 1.005, 0], [0, 90, 0]);
  const R = grp(P, [0, 0, 0], [0, 0, cfg.roll || 0]);
  const B = grp(R, [0, 0, 0], [-90, 0, 0]);
  B.add(Body(cfg.pose));
  const x = cfg.tx, tilt = (cfg.tilt || 0) * D;
  const end = V(x, 0.845, 0);
  if (cfg.under) flatDetector(scene, x, 0.82, 0, cfg.dsz ? cfg.dsz[0] : 0.35, cfg.dsz ? cfg.dsz[1] : 0.43);
  else flatDetector(scene, x, 0.93, 0, cfg.dsz[0], cfg.dsz[1]);
  const topY = 1.0 + cfg.sid - 0.2;
  const tp = V(x + Math.tan(tilt) * (topY - 0.9), topY, 0);
  const crp = V(x, cfg.crY || 1.12, 0);
  tube(scene, tp, end);
  beam(scene, tp, crp, end, cfg.field);
  return scene;
}
function seated(cfg) {
  const scene = new THREE.Scene(); room(scene);
  // كرسي وترابيزة
  mesh(new THREE.BoxGeometry(0.42, 0.04, 0.42), metalDark, [0, 0.43, -0.56], scene);
  for (const [dx, dz] of [[-.17, -.4], [.17, -.4], [-.17, -.72], [.17, -.72]])
    mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.43, 12), metalLight, [dx, 0.215, dz], scene);
  mesh(new THREE.BoxGeometry(1.0, 0.04, 0.72), woodMat, [0, 0.75, 0.0], scene);
  mesh(new THREE.BoxGeometry(0.08, 0.75, 0.08), metalLight, [0, 0.375, 0.1], scene);
  mesh(new THREE.BoxGeometry(0.7, 0.04, 0.5), metalDark, [0, 0.02, 0.1], scene);
  mesh(new THREE.BoxGeometry(0.6, 0.012, 0.5), padMat, [0, 0.776, 0.0], scene);
  const holder = grp(scene, [0, 0.55, -0.56], [0, 0, 0]);
  holder.add(Body({
    lHip: [-90, 0, 0], rHip: [-90, 0, 0], lKn: [90, 0, 0], rKn: [90, 0, 0],
    lSh: [-50, 0, 0], lEl: [-40, 90, 0], rSh: [-10, 0, 0], rEl: [-30, 0, 0],
  }));
  const ax = 0.215, y = 0.80;
  flatDetector(scene, ax, 0.79, cfg.dz, cfg.dsz[0], cfg.dsz[1]);
  const tp = V(ax, 0.80 + cfg.sid - 0.15, cfg.dz);
  const end = V(ax, 0.80, cfg.dz);
  tube(scene, tp, end);
  beam(scene, tp, V(ax, 0.84, cfg.dz), end, cfg.field);
  return scene;
}

// تعريف الفحوصات
const SC = {};
const armsHips = { lSh: [0, 0, 30], lEl: [-95, 0, 0], rSh: [0, 0, 30], rEl: [-95, 0, 0] };
SC.chest_pa = () => standing({ px: FRONT - 0.125, ry: 90, detY: 1.25, crY: 1.30, sid: 1.8, field: 0.40,
  pose: { lSh: [0, 0, 40], lEl: [0, 0, -100], rSh: [0, 0, 40], rEl: [0, 0, -100], head: [-8, 0, 0] } });
SC.chest_lat = () => standing({ px: FRONT - 0.20, detY: 1.25, crY: 1.30, sid: 1.8, field: 0.40,
  pose: { lSh: [-165, 0, 8], lEl: [-25, 0, 0], rSh: [-165, 0, -8], rEl: [-25, 0, 0] } });
SC.shoulder_ap = () => standing({ px: FRONT - 0.125, ry: -90 + 18, detY: 1.38, crY: 1.40, sid: 1.0, field: 0.26,
  pose: { lSh: [0, 0, 28], lEl: [-8, 0, 0], rSh: [0, 0, 6] } });
SC.skull_lat = () => standing({ px: FRONT - 0.20, detY: 1.62, crY: 1.68, sid: 1.0, field: 0.30,
  pose: { lSh: [0, 0, 6], rSh: [0, 0, -6] } });
SC.cspine_lat = () => standing({ px: FRONT - 0.20, detY: 1.5, crY: 1.53, sid: 1.8, field: 0.22,
  pose: { lSh: [0, 0, 5], rSh: [0, 0, -5] } });
const flat = { lHip: [0, 0, -4], rHip: [0, 0, 4], lSh: [0, 0, 10], rSh: [0, 0, 10] };
SC.abdomen_ap = () => lying({ xr: -0.1, tx: -0.2, sid: 1.0, field: 0.40, crY: 1.17, under: true, dsz: [0.43, 0.35],
  pose: { lSh: [0, 0, 12], rSh: [0, 0, 12], lKn: [0, 0, 0], lHip: [0, 0, -4], rHip: [0, 0, 4] } });
SC.pelvis_ap = () => lying({ xr: -0.1, tx: -0.06, sid: 1.0, field: 0.40, crY: 1.14, under: true, dsz: [0.43, 0.35],
  pose: { lSh: [0, 0, 12], rSh: [0, 0, 12], lHip: [0, 12, -4], rHip: [0, 12, 4] } });
SC.lspine_ap = () => lying({ xr: -0.1, tx: -0.22, sid: 1.0, field: 0.34, crY: 1.17, under: true, dsz: [0.43, 0.35],
  pose: { lSh: [0, 0, 12], rSh: [0, 0, 12], lHip: [-50, 0, -4], rHip: [-50, 0, 4], lKn: [95, 0, 0], rKn: [95, 0, 0] } });
SC.lspine_lat = () => lying({ xr: -0.1, tx: -0.2, sid: 1.0, field: 0.36, crY: 1.2, under: true, roll: 90, yr: 1.07, dsz: [0.43, 0.35],
  pose: { lSh: [-150, 0, 0], rSh: [-150, 0, 0], lHip: [-60, 0, 0], rHip: [-60, 0, 0], lKn: [90, 0, 0], rKn: [90, 0, 0] } });
const legsFlat = { lSh: [0, 0, 10], rSh: [0, 0, 10], lHip: [0, 0, -3], rHip: [0, 0, 3] };
SC.knee_ap = () => lying({ xr: -0.15, tx: 0.30, sid: 1.0, field: 0.22, crY: 1.0, dsz: [0.30, 0.36], pose: legsFlat });
SC.ankle_ap = () => lying({ xr: -0.15, tx: 0.72, sid: 1.0, field: 0.20, crY: 1.0, dsz: [0.30, 0.36],
  pose: { ...legsFlat, lAn: [-90, 0, 0] } });
SC.foot_ap = () => lying({ xr: -0.15, tx: 0.80, sid: 1.0, field: 0.22, crY: 1.0, tilt: 10, dsz: [0.30, 0.36],
  pose: { ...legsFlat, lAn: [-60, 0, 0] } });
SC.knee_lat = () => lying({ xr: -0.15, tx: 0.24, sid: 1.0, field: 0.22, crY: 1.07, tilt: 6, roll: 90, yr: 1.07, dsz: [0.30, 0.36],
  pose: { lSh: [-80, 0, 0], rSh: [-80, 0, 0], lHip: [-25, 0, 0], rHip: [-35, 0, 0], lKn: [28, 0, 0], rKn: [50, 0, 0] } });
SC.shoulder_dummy = null;
SC.elbow_ap = () => seated({ dz: -0.33, sid: 1.0, field: 0.22, dsz: [0.30, 0.24] });
SC.wrist_pa = () => seated({ dz: -0.08, sid: 1.0, field: 0.20, dsz: [0.24, 0.30] });
SC.hand_pa = () => seated({ dz: 0.02, sid: 1.0, field: 0.24, dsz: [0.24, 0.30] });

const CAM = {
  chest_pa: [[-0.55, 1.3, 4.6], [-0.7, 0.92, 0]], chest_lat: [[-0.55, 1.3, 4.6], [-0.7, 0.92, 0]],
  shoulder_ap: [[-0.3, 1.3, 4.3], [-0.35, 0.95, 0]],
  skull_lat: [[-0.3, 1.3, 4.2], [-0.3, 0.95, 0]], cspine_lat: [[-0.55, 1.35, 4.4], [-0.7, 1.0, 0]],
  abdomen_ap: [[0.9, 2.1, 2.7], [-0.1, 0.95, 0]], pelvis_ap: [[0.9, 2.1, 2.7], [-0.1, 0.95, 0]],
  lspine_ap: [[0.9, 2.1, 2.7], [-0.1, 0.95, 0]], lspine_lat: [[0.9, 2.1, 2.7], [-0.1, 0.95, 0]],
  knee_ap: [[1.5, 2.0, 3.0], [0.15, 1.15, 0]], ankle_ap: [[1.7, 2.0, 2.9], [0.3, 1.15, 0]],
  foot_ap: [[1.7, 2.0, 2.9], [0.3, 1.15, 0]], knee_lat: [[1.5, 2.0, 3.0], [0.1, 1.15, 0]],
  elbow_ap: [[2.3, 1.5, 1.2], [0, 1.0, -0.2]], wrist_pa: [[2.3, 1.5, 1.2], [0, 1.0, -0.2]],
  hand_pa: [[2.3, 1.5, 1.2], [0, 1.0, -0.2]],
};

window.renderScene = (id) => {
  const scene = SC[id]();
  const [cp, ct] = CAM[id];
  const cam = new THREE.PerspectiveCamera(33, W / H, 0.1, 40);
  cam.position.set(...cp); cam.lookAt(...ct);
  renderer.render(scene, cam);
  window.__done = id;
};
window.__ready = true;
