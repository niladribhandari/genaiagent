#!/usr/bin/env node

/**
 * Test script for the modular MCP server
 * Tests all major functionality to ensure the refactoring was successful
 */

import fetch from 'node-fetch';

const SERVER_URL = 'http://localhost:3001';

async function testEndpoint(name, path, method = 'GET', body = null) {
  console.log(`\n🧪 Testing ${name}...`);
  
  try {
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };
    
    if (body) {
      options.body = JSON.stringify(body);
    }
    
    const response = await fetch(`${SERVER_URL}${path}`, options);
    const data = await response.json();
    
    if (response.ok) {
      console.log(`✅ ${name} - SUCCESS`);
      console.log(`   Response: ${JSON.stringify(data).substring(0, 100)}...`);
    } else {
      console.log(`❌ ${name} - FAILED`);
      console.log(`   Error: ${data.error || 'Unknown error'}`);
    }
    
    return { success: response.ok, data };
  } catch (error) {
    console.log(`💥 ${name} - ERROR`);
    console.log(`   ${error.message}`);
    return { success: false, error: error.message };
  }
}

async function runTests() {
  console.log('🚀 Starting Modular MCP Server Tests\n');
  
  const tests = [
    // Basic endpoints
    ['Health Check', '/'],
    ['Health Status', '/health'],
    ['Tools List', '/tools'],
    
    // Project tools
    ['List Generated Projects', '/tools/list_generated_projects', 'POST', {}],
    ['Analyze Project Structure', '/tools/analyze_project_structure', 'POST', {
      projectPath: '/Users/niladrib/WorkingFolder/genaiagent/mcp-server',
      maxDepth: 2
    }],
    
    // Workflow tools
    ['List Workflows', '/tools/list_workflows', 'POST', {}],
    ['Get Pending Approvals', '/tools/get_pending_approvals', 'POST', {}],
  ];
  
  let passed = 0;
  let total = tests.length;
  
  for (const [name, path, method, body] of tests) {
    const result = await testEndpoint(name, path, method, body);
    if (result.success) {
      passed++;
    }
    
    // Small delay between tests
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  console.log(`\n📊 Test Results: ${passed}/${total} passed`);
  
  if (passed === total) {
    console.log('🎉 All tests passed! The modular server is working correctly.');
  } else {
    console.log('⚠️  Some tests failed. Please check the server logs.');
  }
}

// Run tests if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runTests().catch(console.error);
}
