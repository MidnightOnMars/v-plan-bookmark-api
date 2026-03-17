#!/usr/bin/env node
'use strict';

const http = require('http');

const baseUrl = process.env.BOOKMARK_API_URL || 'http://localhost:9877';
const parsed = new URL(baseUrl);
const hostname = parsed.hostname;
const port = parseInt(parsed.port, 10) || 80;

function request(method, path, body) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname,
      port,
      path,
      method,
      headers: {},
    };

    if (body !== undefined) {
      const data = JSON.stringify(body);
      options.headers['Content-Type'] = 'application/json';
      options.headers['Content-Length'] = Buffer.byteLength(data);
    }

    const req = http.request(options, (res) => {
      let chunks = '';
      res.on('data', (chunk) => { chunks += chunk; });
      res.on('end', () => {
        let parsed;
        try {
          parsed = JSON.parse(chunks);
        } catch (e) {
          parsed = chunks;
        }
        resolve({ status: res.statusCode, data: parsed });
      });
    });

    req.on('error', (err) => {
      reject(err);
    });

    if (body !== undefined) {
      req.write(JSON.stringify(body));
    }
    req.end();
  });
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command) {
    console.error('Usage: node client/index.js <command> [args]');
    process.exit(1);
  }

  let result;

  switch (command) {
    case 'list': {
      result = await request('GET', '/bookmarks');
      break;
    }
    case 'add': {
      const url = args[1];
      const title = args[2];
      if (!url || !title) {
        console.error('Usage: node client/index.js add <url> <title> [--tags tag1,tag2]');
        process.exit(1);
      }
      let tags = [];
      const tagsIdx = args.indexOf('--tags');
      if (tagsIdx !== -1 && args[tagsIdx + 1]) {
        tags = args[tagsIdx + 1].split(',');
      }
      result = await request('POST', '/bookmarks', { url, title, tags });
      break;
    }
    case 'get': {
      const id = args[1];
      if (!id) {
        console.error('Usage: node client/index.js get <id>');
        process.exit(1);
      }
      result = await request('GET', `/bookmarks/${id}`);
      break;
    }
    case 'delete': {
      const id = args[1];
      if (!id) {
        console.error('Usage: node client/index.js delete <id>');
        process.exit(1);
      }
      result = await request('DELETE', `/bookmarks/${id}`);
      break;
    }
    case 'search': {
      const tag = args[1];
      if (!tag) {
        console.error('Usage: node client/index.js search <tag>');
        process.exit(1);
      }
      result = await request('GET', `/bookmarks/search?tag=${encodeURIComponent(tag)}`);
      break;
    }
    default: {
      console.error(`Unknown command: ${command}`);
      process.exit(1);
    }
  }

  process.stdout.write(JSON.stringify(result.data) + '\n');

  if (result.status >= 400) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
