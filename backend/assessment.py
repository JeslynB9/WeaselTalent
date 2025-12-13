<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Backend Assessments</title>
  <style>
    :root { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; }
    body { margin: 0; background: #0b0f19; color: #e9eefc; }
    .wrap { max-width: 920px; margin: 0 auto; padding: 28px 16px 60px; }
    .card { background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.12); border-radius: 16px; padding: 18px; }
    h1 { margin: 0 0 10px; font-size: 28px; }
    p { margin: 8px 0 0; color: rgba(233,238,252,.82); }
    .row { display: grid; grid-template-columns: 1fr 1fr auto; gap: 10px; margin-top: 14px; }
    select, button {
      border-radius: 12px; border: 1px solid rgba(255,255,255,.16);
      background: rgba(0,0,0,.2); color: #e9eefc; padding: 12px 12px;
      font-size: 14px;
    }
    button { cursor: pointer; background: rgba(107, 88, 255, .35); }
    button:hover { background: rgba(107, 88, 255, .5); }
    button:disabled { opacity: .45; cursor: not-allowed; }
    .muted { color: rgba(233,238,252,.7); font-size: 13px; }
    .spacer { height: 14px; }
    .q { margin-top: 16px; padding: 14px; border-radius: 14px; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.10); }
    .q h3 { margin: 0 0 10px; font-size: 16px; }
    .opt { display: grid; gap: 8px; margin: 8px 0; }
    label {
      display: flex; gap: 10px; align-items: flex-start;
      padding: 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,.10);
      background: rgba(0,0,0,.18);
      cursor: pointer;
    }
    label:hover { border-color: rgba(255,255,255,.18); }
    input[type="radio"] { margin-top: 3px; }
    .actions { display: flex; gap: 10px; margin-top: 16px; flex-wrap: wrap; }
    .pill { display: inline-flex; gap: 8px; align-items: center; padding: 8px 10px; border-radius: 999px;
            border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.05); font-size: 13px; }
    .result { margin-top: 18px; padding: 14px; border-radius: 14px; border: 1px solid rgba(255,255,255,.14); background: rgba(0,0,0,.22); }
    .ok { color: #b7ffcf; }
    .bad { color: #ffc3c3; }
    .explain { margin-top: 8px; color: rgba(233,238,252,.78); font-size: 14px; }
    .hidden { display: none; }
  </style>
</head>

<body>
  <div class="wrap">
    <div class="card">
      <h1>Backend Assessments</h1>
      <p>Pick a domain + level. Complete the quiz. Get a score + feedback.</p>

      <div class="row">
        <select id="domain">
          <option value="Node.js">Node.js (Backend)</option>
          <option value="SQL">SQL</option>
          <option value="APIs">APIs / REST</option>
          <option value="C++ Backend">C++ Backend</option>
        </select>

        <select id="level">
          <option value="1">Level 1 (Basics)</option>
          <option value="2">Level 2 (Intermediate)</option>
          <option value="3">Level 3 (Advanced)</option>
          <option value="4">Level 4 (Expert)</option>
        </select>

        <button id="startBtn">Start</button>
      </div>

      <div class="spacer"></div>
      <div class="muted">D

