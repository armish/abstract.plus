#!/usr/bin/env python3
"""
ESMO 2025 Abstract Annotator - Conference Web Application
Run this single file to start the web application.

Usage:
    python conference-webapp.py
"""

import os
import json
import pandas as pd
from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import random
import hashlib
from datetime import datetime, timedelta
import io
import gc

# HTML Template embedded as string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESMO 2025 Abstract Annotator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }
        
        .container {
            max-width: 95%;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background-color: #2c3e50;
            color: white;
            padding: 20px 0;
            margin-bottom: 30px;
        }
        
        h1 {
            text-align: center;
            font-size: 2rem;
        }
        
        .stats {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: flex;
            justify-content: space-around;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #3498db;
        }
        
        .controls {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .search-box {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .annotate-box {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .advanced-settings {
            margin-top: 15px;
            border-top: 1px solid #eee;
            padding-top: 15px;
        }
        
        .settings-toggle {
            cursor: pointer;
            color: #3498db;
            font-weight: 500;
            margin-bottom: 10px;
            display: inline-block;
        }
        
        .settings-toggle:hover {
            color: #2980b9;
        }
        
        .settings-content {
            display: none;
            margin-top: 10px;
        }
        
        .settings-content.show {
            display: block;
        }
        
        .control-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: background-color 0.2s;
        }
        
        .btn-primary {
            background-color: #3498db;
            color: white;
        }
        
        .btn-primary:hover {
            background-color: #2980b9;
        }
        
        .btn-secondary {
            background-color: #95a5a6;
            color: white;
        }
        
        .btn-secondary:hover {
            background-color: #7f8c8d;
        }
        
        .btn-success {
            background-color: #27ae60;
            color: white;
        }
        
        .btn-success:hover {
            background-color: #229954;
        }
        
        .table-container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow-x: auto;
            width: 100%;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            table-layout: auto;
            min-width: 1200px; /* Ensure table has minimum width for all columns */
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
            border-right: 1px solid #eee;
            position: relative;
            overflow: hidden;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: 600;
            position: sticky;
            top: 0;
            user-select: none;
        }
        
        th:last-child, td:last-child {
            border-right: none;
        }
        
        tr:hover {
            background-color: #f8f9fa;
        }
        
        /* Column widths for new order */
        th:nth-child(1), td:nth-child(1) { /* Abstract # */
            width: 80px;
            min-width: 80px;
        }

        th:nth-child(2), td:nth-child(2) { /* Track */
            width: 150px;
            min-width: 120px;
        }

        th:nth-child(3), td:nth-child(3) { /* Author */
            width: 120px;
            min-width: 100px;
        }

        th:nth-child(4), td:nth-child(4) { /* Abstract title */
            width: 200px;
            min-width: 150px;
        }

        th:nth-child(5), td:nth-child(5) { /* Abstract */
            width: 300px;
            min-width: 250px;
        }

        th:nth-child(6), td:nth-child(6) { /* Matched Keywords */
            width: 120px;
            min-width: 100px;
            background-color: #fff3cd;
        }

        td:nth-child(6) {
            background-color: #fffbf0;
            font-style: italic;
        }

        /* Annotation columns */
        th:nth-child(7), td:nth-child(7),
        th:nth-child(8), td:nth-child(8) {
            width: 150px;
            min-width: 120px;
        }
        
        .abstract-cell {
            position: relative;
            padding-right: 60px;
            max-width: 250px;
        }
        
        .abstract-preview {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            display: block;
            max-width: calc(100% - 30px);
        }
        
        .abstract-cell.expanded .abstract-preview {
            white-space: normal;
            word-wrap: break-word;
            overflow: visible;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            line-height: 1.5;
            max-height: 300px;
            overflow-y: auto;
            max-width: 400px;
        }
        
        .expand-button {
            position: absolute;
            right: 30px;
            top: 50%;
            transform: translateY(-50%);
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 3px;
            padding: 2px 6px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
            z-index: 10;
            line-height: 1;
        }

        .expand-button:hover {
            background-color: #2980b9;
        }

        .abstract-cell.expanded .expand-button {
            top: 12px;
            transform: none;
        }

        .modal-button {
            position: absolute;
            right: 5px;
            top: 50%;
            transform: translateY(-50%);
            background-color: #9b59b6;
            color: white;
            border: none;
            border-radius: 3px;
            padding: 2px 6px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
            z-index: 10;
            line-height: 1;
        }

        .modal-button:hover {
            background-color: #8e44ad;
        }

        .abstract-cell.expanded .modal-button {
            top: 12px;
            transform: none;
        }
        
        .pagination {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            margin-top: 20px;
        }
        
        .page-info {
            margin: 0 20px;
        }
        
        .progress-container {
            display: none;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .progress-bar {
            width: 100%;
            height: 30px;
            background-color: #ecf0f1;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background-color: #3498db;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.7);
            overflow: auto;
        }

        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 8px;
            width: 90%;
            max-width: 900px;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #eee;
        }

        .modal-title {
            font-size: 1.3rem;
            font-weight: bold;
            color: #2c3e50;
            flex: 1;
            margin-right: 20px;
        }

        .close {
            color: #aaa;
            font-size: 32px;
            font-weight: bold;
            cursor: pointer;
            line-height: 1;
            transition: color 0.2s;
        }

        .close:hover {
            color: #000;
        }

        .modal-abstract-text {
            line-height: 1.8;
            font-size: 1rem;
            color: #333;
            white-space: pre-wrap;
        }

        .modal-abstract-text strong {
            color: #2c3e50;
            font-weight: 700;
        }

        .keyword-highlight {
            background-color: #ffeb3b;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: 500;
        }

        .modal-info {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 0.95rem;
        }

        .modal-info-item {
            margin-bottom: 8px;
        }

        .modal-info-label {
            font-weight: 600;
            color: #555;
            display: inline-block;
            min-width: 100px;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .checkbox-group input {
            width: auto;
        }
        
        .error {
            color: #e74c3c;
            margin-top: 10px;
        }
        
        .success {
            color: #27ae60;
            margin-top: 10px;
        }
        
        input[type="file"] {
            padding: 4px;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>ESMO 2025 Abstract Annotator</h1>
            <div style="text-align: center; margin-top: 10px;">
                <a href="https://cslide.ctimeetingtech.com/esmo2025/attendee/confcal" target="_blank" style="color: #ecf0f1; text-decoration: none; font-size: 0.9rem;">
                    View Original ESMO 2025 Conference →
                </a>
            </div>
        </div>
    </header>
    
    <div class="container">
        <!-- Statistics -->
        <div class="stats" id="stats">
            <div class="stat-item">
                <div class="stat-value" id="totalAbstracts">-</div>
                <div>Filtered Abstracts</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="abstractsWithText">-</div>
                <div>With Abstract Text</div>
            </div>
        </div>
        
        <!-- Search Box -->
        <div class="search-box">
            <div class="control-group">
                <label for="searchInput">Search Abstracts (separate multiple keywords with semicolon):</label>
                <input type="text" id="searchInput" placeholder="e.g., breast cancer; immunotherapy; PD-L1" onkeypress="handleSearchKeyPress(event)">
            </div>
            
            <div class="button-group">
                <button class="btn-primary" onclick="searchAbstracts()">Search</button>
                <button class="btn-secondary" onclick="resetSearch()">Reset Search</button>
            </div>
            
            <div id="searchMessage" style="margin-top: 10px;"></div>
        </div>
        
        <!-- Annotation Box -->
        <div class="annotate-box">
            <h3>Annotation Settings</h3>
            
            <div class="control-group">
                <label for="questionInput">Annotation Question:</label>
                <textarea id="questionInput" placeholder="Enter the question you want to ask about each abstract (e.g. what is the treatment modality?)"></textarea>
            </div>
            
            <div class="advanced-settings">
                <div class="settings-toggle" onclick="toggleAnnotationSettings()">
                    ▶ Advanced Settings
                </div>
                <div class="settings-content" id="annotationAdvancedSettings">
                    <div class="control-group">
                        <label for="modelSelect">Model:</label>
                        <select id="modelSelect">
                            <option value="gpt-5-nano" selected>GPT-5 Nano - Most cost-effective (default)</option>
                            <option value="gpt-5-mini">GPT-5 Mini - Fast and affordable</option>
                            <option value="gpt-5">GPT-5 - Smartest, fastest model with thinking built in</option>
                            <option value="gpt-4o">GPT-4o - Multimodal text and images</option>
                            <option value="gpt-4o-mini">GPT-4o mini - Fast, affordable small model</option>
                            <option value="gpt-4-turbo">GPT-4 Turbo</option>
                            <option value="gpt-4">GPT-4</option>
                        </select>
                    </div>
                    
                    <div class="control-group">
                        <label for="apiKey">OpenAI API Key:</label>
                        <input type="password" id="apiKey" placeholder="sk-..." value="{{ openai_api_key }}">
                    </div>
                    
                    <div class="control-group">
                        <label for="numThreads">Number of Threads:</label>
                        <input type="number" id="numThreads" min="1" max="200" value="100">
                    </div>
                    
                    <div class="control-group">
                        <label for="perPage">Results per page:</label>
                        <select id="perPage">
                            <option value="10">10</option>
                            <option value="20" selected>20</option>
                            <option value="50">50</option>
                            <option value="100">100</option>
                            <option value="200">200</option>
                        </select>
                    </div>
                    
                    <div class="checkbox-group">
                        <input type="checkbox" id="dryRun">
                        <label for="dryRun">Dry Run (no API calls)</label>
                    </div>
                    
                    <div class="checkbox-group">
                        <input type="checkbox" id="showEmptyAbstracts" checked>
                        <label for="showEmptyAbstracts">Show rows without abstract text</label>
                    </div>
                </div>
            </div>
            
            <div class="button-group">
                <button class="btn-success" onclick="startAnnotation()">Start Annotation</button>
            </div>
            
            <div id="message" class="error"></div>
        </div>
        
        <!-- Progress Bar -->
        <div class="progress-container" id="progressContainer">
            <h3>Annotation Progress</h3>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill">0%</div>
            </div>
            <div id="progressText">Processing...</div>
        </div>
        
        <!-- Table -->
        <div class="table-container">
            <table id="abstractsTable">
                <thead>
                    <tr>
                        <th>Abstract #</th>
                        <th>Title</th>
                        <th>First Author</th>
                        <th>Track</th>
                        <th>Abstract</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                    <!-- Data will be populated here -->
                </tbody>
            </table>
            
            <div class="pagination">
                <button onclick="previousPage()" id="prevBtn">Previous</button>
                <span class="page-info" id="pageInfo">Page 1 of 1</span>
                <button onclick="nextPage()" id="nextBtn">Next</button>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <button class="btn-success" id="downloadButton" onclick="downloadResults()">Download Results</button>
            </div>
        </div>
    </div>

    <!-- Abstract Modal -->
    <div id="abstractModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title" id="modalTitle"></div>
                <span class="close" onclick="closeAbstractModal()">&times;</span>
            </div>
            <div class="modal-info" id="modalInfo"></div>
            <div class="modal-abstract-text" id="modalAbstractText"></div>
        </div>
    </div>

    <script>
        let currentPage = 1;
        let totalPages = 1;
        let currentTaskId = null;
        let progressInterval = null;
        let isShowingAnnotated = false;
        let currentFilteredTotal = 0;  // Track filtered total
        
        // Load statistics on page load
        window.onload = function() {
            loadStats();
            loadAbstracts();
            
            // Add event listeners
            document.getElementById('showEmptyAbstracts').addEventListener('change', function() {
                loadAbstracts(1);  // Reload from page 1 when toggling
            });
            
            document.getElementById('perPage').addEventListener('change', function() {
                loadAbstracts(1);  // Reload from page 1 when changing per page
            });
        };
        
        function handleSearchKeyPress(event) {
            if (event.key === 'Enter') {
                searchAbstracts();
            }
        }
        
        function toggleAbstract(button) {
            const cell = button.closest('.abstract-cell');
            const preview = cell.querySelector('.abstract-preview');

            if (cell.classList.contains('expanded')) {
                cell.classList.remove('expanded');
                button.textContent = '+';
                button.style.top = '50%';
                button.style.transform = 'translateY(-50%)';
            } else {
                // Get the original text and apply formatting
                const originalText = preview.getAttribute('data-original-text');
                if (originalText && !preview.getAttribute('data-formatted')) {
                    const formattedText = formatAbstractText(originalText);
                    preview.innerHTML = formattedText;
                    preview.setAttribute('data-formatted', 'true');
                }

                cell.classList.add('expanded');
                button.textContent = '−';
                button.style.top = '12px';
                button.style.transform = 'none';
            }
        }
        
        function toggleAnnotationSettings() {
            const settings = document.getElementById('annotationAdvancedSettings');
            const toggle = document.querySelector('.annotate-box .settings-toggle');
            
            if (settings.classList.contains('show')) {
                settings.classList.remove('show');
                toggle.innerHTML = '▶ Advanced Settings';
            } else {
                settings.classList.add('show');
                toggle.innerHTML = '▼ Advanced Settings';
            }
        }
        
        function resetSearch() {
            document.getElementById('searchInput').value = '';
            document.getElementById('searchMessage').innerHTML = '';
            loadAbstracts(1);
        }
        
        function showSearchMessage(message, type = 'info') {
            const messageEl = document.getElementById('searchMessage');
            messageEl.className = type;
            messageEl.textContent = message;
            setTimeout(() => {
                messageEl.textContent = '';
            }, 5000);
        }
        
        function showMessage(message, type = 'error') {
            const messageEl = document.getElementById('message');
            messageEl.className = type;
            messageEl.textContent = message;
            
            // Add download button if annotation is complete
            if (message.includes('completed successfully') && currentTaskId) {
                messageEl.innerHTML = message + ' <button class="btn-success" style="margin-left: 10px;" onclick="downloadResults()">Download Now</button>';
            }
            
            setTimeout(() => {
                messageEl.textContent = '';
            }, 10000); // Show for longer when download is available
        }
        
        function loadStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('totalAbstracts').textContent = data.total_abstracts.toLocaleString();
                    document.getElementById('abstractsWithText').textContent = data.abstracts_with_text.toLocaleString();
                })
                .catch(error => console.error('Error loading stats:', error));
        }
        
        function loadAbstracts(page = 1) {
            const search = document.getElementById('searchInput').value;
            const showEmpty = document.getElementById('showEmptyAbstracts').checked;
            const perPage = document.getElementById('perPage').value;
            
            fetch('/api/abstracts?page=' + page + '&per_page=' + perPage + '&search=' + encodeURIComponent(search) + '&show_empty=' + showEmpty)
                .then(response => response.json())
                .then(data => {
                    currentPage = data.page;
                    totalPages = data.total_pages;
                    isShowingAnnotated = false;
                    currentFilteredTotal = data.total;  // Store filtered total
                    
                    // Update filtered count in stats
                    document.getElementById('totalAbstracts').textContent = data.total.toLocaleString();
                    
                    // Update table
                    const tbody = document.getElementById('tableBody');
                    tbody.innerHTML = '';
                    
                    // Reset table headers to default
                    const thead = document.querySelector('#abstractsTable thead tr');
                    thead.innerHTML = '<th>Abstract #</th><th>Track</th><th>Author</th><th>Abstract Title</th><th>Abstract</th>' +
                        (search ? '<th>Matched Keywords</th>' : '');
                    
                    data.data.forEach(row => {
                        const tr = document.createElement('tr');
                        const abstractText = row['Abstract'] || '';
                        const hasAbstract = abstractText && abstractText !== '-' && abstractText !== '0';
                        
                        // Escape HTML in abstract text
                        const escapeHtml = (text) => {
                            const div = document.createElement('div');
                            div.textContent = text;
                            return div.innerHTML;
                        };
                        
                        tr.innerHTML = '<td>' + (row['Abstract #'] || '-') + '</td>' +
                            '<td>' + (row['Track'] || '-') + '</td>' +
                            '<td>' + (row['First Author'] || '-') + '</td>' +
                            '<td>' + (row['Abstract title'] || '-') + '</td>' +
                            '<td class="abstract-cell">' +
                                (hasAbstract ?
                                    '<div class="abstract-preview" data-original-text="' + escapeHtml(abstractText) + '">' + escapeHtml(abstractText) + '</div>' +
                                    '<button class="expand-button" onclick="toggleAbstract(this)">+</button>' +
                                    '<button class="modal-button" onclick="openModal(this)" title="Open in modal view">⊡</button>' :
                                    '-') +
                            '</td>' +
                            (search && row['Matched Keywords'] ? '<td>' + escapeHtml(row['Matched Keywords']) + '</td>' : (search ? '<td>-</td>' : ''));

                        // Store row data for modal access
                        if (hasAbstract) {
                            const abstractCell = tr.querySelector('.abstract-cell');
                            abstractCell.dataset.rowData = JSON.stringify(row);
                        }

                        tbody.appendChild(tr);
                    });
                    
                    // Update pagination
                    document.getElementById('pageInfo').textContent = 'Page ' + currentPage + ' of ' + totalPages;
                    document.getElementById('prevBtn').disabled = currentPage === 1;
                    document.getElementById('nextBtn').disabled = currentPage === totalPages;
                    
                    // Show search complete message
                    if (search) {
                        showSearchMessage('Search complete! Found ' + data.total + ' matching abstracts.', 'success');
                    }
                })
                .catch(error => console.error('Error loading abstracts:', error));
        }
        
        function searchAbstracts() {
            isShowingAnnotated = false;
            currentTaskId = null;
            loadAbstracts(1);
        }
        
        function previousPage() {
            if (currentPage > 1) {
                if (isShowingAnnotated && currentTaskId) {
                    loadAnnotatedResults(currentPage - 1);
                } else {
                    loadAbstracts(currentPage - 1);
                }
            }
        }
        
        function nextPage() {
            if (currentPage < totalPages) {
                if (isShowingAnnotated && currentTaskId) {
                    loadAnnotatedResults(currentPage + 1);
                } else {
                    loadAbstracts(currentPage + 1);
                }
            }
        }
        
        function startAnnotation() {
            const question = document.getElementById('questionInput').value.trim();
            const apiKey = document.getElementById('apiKey').value.trim();
            const model = document.getElementById('modelSelect').value;
            const numThreads = parseInt(document.getElementById('numThreads').value);
            const dryRun = document.getElementById('dryRun').checked;
            const searchFilter = document.getElementById('searchInput').value;
            const showEmpty = document.getElementById('showEmptyAbstracts').checked;
            
            if (!question) {
                showMessage('Please enter a question to ask about the abstracts', 'error');
                return;
            }
            
            if (!dryRun && !apiKey) {
                showMessage('Please enter your OpenAI API key or enable dry run', 'error');
                return;
            }
            
            // Show progress container
            document.getElementById('progressContainer').style.display = 'block';
            document.getElementById('progressFill').style.width = '0%';
            document.getElementById('progressFill').textContent = '0%';
            
            const requestData = {
                question: question,
                api_key: apiKey,
                model: model,
                num_threads: numThreads,
                dry_run: dryRun,
                search_filter: searchFilter,
                show_empty: showEmpty
            };
            
            fetch('/api/annotate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.task_id) {
                    currentTaskId = data.task_id;
                    document.getElementById('progressText').textContent = 'Processing ' + data.total + ' abstracts...';
                    startProgressTracking();
                } else {
                    showMessage('Failed to start annotation', 'error');
                }
            })
            .catch(error => {
                showMessage('Error: ' + error, 'error');
                document.getElementById('progressContainer').style.display = 'none';
            });
        }
        
        function startProgressTracking() {
            if (progressInterval) {
                clearInterval(progressInterval);
            }

            progressInterval = setInterval(() => {
                if (!currentTaskId) return;

                fetch('/api/progress/' + currentTaskId)
                    .then(response => response.json())
                    .then(data => {
                        // Safely calculate percentage, avoiding NaN
                        let percentage = 0;
                        if (data.total && data.total > 0) {
                            percentage = Math.round((data.completed / data.total) * 100);
                            // Clamp between 0 and 100
                            percentage = Math.max(0, Math.min(100, percentage));
                        }

                        document.getElementById('progressFill').style.width = percentage + '%';
                        document.getElementById('progressFill').textContent = percentage + '%';

                        if (data.status === 'completed') {
                            clearInterval(progressInterval);
                            document.getElementById('progressFill').style.width = '100%';
                            document.getElementById('progressFill').textContent = '100%';
                            document.getElementById('progressText').textContent = 'Annotation completed!';
                            showMessage('Annotation completed successfully!', 'success');

                            // Reload the table to show the new annotation column
                            loadAnnotatedResults();
                        }
                    })
                    .catch(error => {
                        console.error('Error tracking progress:', error);
                    });
            }, 1000);
        }
        
        function loadAnnotatedResults(page = 1) {
            // Load the annotated results and update the table
            if (!currentTaskId) return;
            
            isShowingAnnotated = true;
            const perPage = document.getElementById('perPage').value;
            
            fetch('/api/annotated/' + currentTaskId + '?page=' + page + '&per_page=' + perPage)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error('Error loading annotated results:', data.error);
                        return;
                    }
                    
                    currentPage = data.page;
                    totalPages = data.total_pages;
                    
                    // Update table headers if new columns exist
                    if (data.columns && data.columns.length > 0) {
                        const thead = document.querySelector('#abstractsTable thead tr');
                        thead.innerHTML = '';
                        
                        // Add standard columns in new order
                        const standardColumns = [
                            {name: 'Abstract #', field: 'Abstract #'},
                            {name: 'Track', field: 'Track'},
                            {name: 'Author', field: 'First Author'},
                            {name: 'Abstract Title', field: 'Abstract title'},
                            {name: 'Abstract', field: 'Abstract'}
                        ];
                        
                        standardColumns.forEach(col => {
                            const th = document.createElement('th');
                            th.textContent = col.name;
                            thead.appendChild(th);
                        });
                        
                        // Add matched keywords column if present
                        if (data.columns.includes('Matched Keywords')) {
                            const th = document.createElement('th');
                            th.textContent = 'Matched Keywords';
                            th.style.backgroundColor = '#fff3cd';
                            thead.appendChild(th);
                        }
                        
                        // Add annotation columns
                        data.columns.forEach(col => {
                            if (col.startsWith('Answer:')) {
                                const th = document.createElement('th');
                                th.textContent = col;
                                th.style.backgroundColor = '#e8f5e9';
                                thead.appendChild(th);
                            }
                        });
                    }
                    
                    // Update table body
                    const tbody = document.getElementById('tableBody');
                    tbody.innerHTML = '';
                    
                    data.data.forEach(row => {
                        const tr = document.createElement('tr');
                        const abstractText = row['Abstract'] || '';
                        const hasAbstract = abstractText && abstractText !== '-' && abstractText !== '0';
                        
                        // Escape HTML in text
                        const escapeHtml = (text) => {
                            const div = document.createElement('div');
                            div.textContent = text;
                            return div.innerHTML;
                        };
                        
                        // Add standard columns with expandable abstract in new order
                        let html = '<td>' + (row['Abstract #'] || '-') + '</td>' +
                            '<td>' + (row['Track'] || '-') + '</td>' +
                            '<td>' + (row['First Author'] || '-') + '</td>' +
                            '<td>' + (row['Abstract title'] || '-') + '</td>' +
                            '<td class="abstract-cell">' +
                                (hasAbstract ?
                                    '<div class="abstract-preview" data-original-text="' + escapeHtml(abstractText) + '">' + escapeHtml(abstractText) + '</div>' +
                                    '<button class="expand-button" onclick="toggleAbstract(this)">+</button>' +
                                    '<button class="modal-button" onclick="openModal(this)" title="Open in modal view">⊡</button>' :
                                    '-') +
                            '</td>';

                        // Add matched keywords if present
                        if (data.columns.includes('Matched Keywords')) {
                            html += '<td style="background-color: #fffbf0; font-style: italic;">' + escapeHtml(row['Matched Keywords'] || '-') + '</td>';
                        }

                        tr.innerHTML = html;

                        // Add annotation columns
                        data.columns.forEach(col => {
                            if (col.startsWith('Answer:')) {
                                const td = document.createElement('td');
                                td.textContent = row[col] || '-';
                                td.style.backgroundColor = '#f1f8e9';
                                tr.appendChild(td);
                            }
                        });

                        // Store row data for modal access
                        if (hasAbstract) {
                            const abstractCell = tr.querySelector('.abstract-cell');
                            abstractCell.dataset.rowData = JSON.stringify(row);
                        }

                        tbody.appendChild(tr);
                    });
                                            
                    // Update pagination
                    document.getElementById('pageInfo').textContent = 'Page ' + data.page + ' of ' + data.total_pages;
                    document.getElementById('prevBtn').disabled = data.page === 1;
                    document.getElementById('nextBtn').disabled = data.page === data.total_pages;
                })
                .catch(error => console.error('Error loading annotated results:', error));
        }
        
        function downloadResults() {
            if (currentTaskId && isShowingAnnotated) {
                // Download annotated results
                window.location.href = '/api/download/' + currentTaskId;
            } else {
                // Download current filtered view
                const search = document.getElementById('searchInput').value;
                const showEmpty = document.getElementById('showEmptyAbstracts').checked;

                window.location.href = '/api/download/current?search=' + encodeURIComponent(search) + '&show_empty=' + showEmpty;
            }
        }

        // Format abstract text with bold section headers
        function formatAbstractText(text) {
            if (!text) return text;

            // Escape HTML first to prevent XSS
            const div = document.createElement('div');
            div.textContent = text;
            let formatted = div.innerHTML;

            // List of section headers to make bold
            const headers = ['Background', 'Methods', 'Results', 'Conclusions', 'Legal entity responsible for the study', 'Disclosure'];

            headers.forEach(header => {
                // Match header at start of text or after period/newline/space
                const regex = new RegExp(`(^|\\. |\\n)(${header})([:  ])`, 'gi');
                formatted = formatted.replace(regex, '$1<strong>$2</strong>$3');
            });

            return formatted;
        }

        // Highlight keywords in text
        function highlightKeywords(text, keywords) {
            if (!text || !keywords) return text;

            let highlighted = text;
            const keywordList = keywords.split(';').map(k => k.trim()).filter(k => k);

            keywordList.forEach(keyword => {
                // Escape special regex characters in the keyword
                const escapedKeyword = keyword.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
                const regex = new RegExp(`(${escapedKeyword})`, 'gi');
                highlighted = highlighted.replace(regex, '<span class="keyword-highlight">$1</span>');
            });

            return highlighted;
        }

        // Open modal from button click
        function openModal(button) {
            const cell = button.closest('.abstract-cell');
            const rowData = JSON.parse(cell.dataset.rowData);
            showAbstractModal(rowData);
        }

        // Show abstract in modal
        function showAbstractModal(row) {
            const modal = document.getElementById('abstractModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalInfo = document.getElementById('modalInfo');
            const modalAbstractText = document.getElementById('modalAbstractText');

            // Set title
            modalTitle.textContent = row['Abstract title'] || 'Abstract';

            // Set info
            let infoHTML = '';
            if (row['Abstract #']) {
                infoHTML += `<div class="modal-info-item"><span class="modal-info-label">Abstract #:</span> ${row['Abstract #']}</div>`;
            }
            if (row['First Author']) {
                infoHTML += `<div class="modal-info-item"><span class="modal-info-label">Author:</span> ${row['First Author']}</div>`;
            }
            if (row['Track']) {
                infoHTML += `<div class="modal-info-item"><span class="modal-info-label">Track:</span> ${row['Track']}</div>`;
            }
            if (row['Matched Keywords']) {
                infoHTML += `<div class="modal-info-item"><span class="modal-info-label">Keywords:</span> ${row['Matched Keywords']}</div>`;
            }
            modalInfo.innerHTML = infoHTML;

            // Set abstract text with formatting
            let abstractText = row['Abstract'] || 'No abstract available';
            abstractText = formatAbstractText(abstractText);

            if (row['Matched Keywords']) {
                abstractText = highlightKeywords(abstractText, row['Matched Keywords']);
            }

            modalAbstractText.innerHTML = abstractText;

            // Show modal
            modal.style.display = 'block';
        }

        // Close modal
        function closeAbstractModal() {
            document.getElementById('abstractModal').style.display = 'none';
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('abstractModal');
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

app = Flask(__name__)
CORS(app)

# Global variables for progress tracking
annotation_progress = {}
annotation_results = {}
annotation_timestamps = {}  # Track creation time for cleanup

# Constants
RESULT_EXPIRATION_HOURS = 24

# Load data at startup
def load_data():
    """Load the Excel file from the same directory as the app"""
    try:
        # Look for the Excel file in the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_files = [
            '2025 ESMO - All combined - raw.xlsx',
            '2025 ESMO Abstracts.xlsx',
            'ESMO_Abstracts.xlsx',
            '2025 ASCO - Abstracts.xlsx',
            '2025 ASCO Abstracts.xlsx',
            'ASCO_Abstracts.xlsx',
            'abstracts.xlsx'
        ]

        df = None
        for filename in possible_files:
            filepath = os.path.join(script_dir, filename)
            if os.path.exists(filepath):
                print(f"Loading Excel file: {filepath}")
                df = pd.read_excel(filepath)
                break

        if df is None:
            # Try to find any .xlsx file in the directory
            xlsx_files = [f for f in os.listdir(script_dir) if f.endswith('.xlsx')]
            if xlsx_files:
                filepath = os.path.join(script_dir, xlsx_files[0])
                print(f"Loading Excel file: {filepath}")
                df = pd.read_excel(filepath)
            else:
                print("ERROR: No Excel file found in the application directory!")
                print(f"Please place your ESMO abstracts Excel file in: {script_dir}")
                return pd.DataFrame()

        # Normalize column names for ESMO format
        # Map ESMO columns to ASCO column names for consistency
        column_mapping = {
            'Poster ID': 'Abstract #',
            'Poster Title': 'Abstract title',
            'Presenting Author': 'First Author',
            'Category': 'Track'
        }

        df = df.rename(columns=column_mapping)

        # Add Link column if it doesn't exist
        if 'Link' not in df.columns:
            df['Link'] = ''

        # Clean data
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('')
            else:
                df[col] = df[col].fillna(0)

        print(f"Successfully loaded {len(df)} abstracts from {os.path.basename(filepath)}")
        print(f"Columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

# Initialize data
abstracts_df = load_data()

def cleanup_old_results():
    """Remove annotation results older than RESULT_EXPIRATION_HOURS"""
    current_time = datetime.now()
    expired_tasks = []

    for task_id, timestamp in annotation_timestamps.items():
        if current_time - timestamp > timedelta(hours=RESULT_EXPIRATION_HOURS):
            expired_tasks.append(task_id)

    for task_id in expired_tasks:
        if task_id in annotation_results:
            del annotation_results[task_id]
        if task_id in annotation_progress:
            del annotation_progress[task_id]
        if task_id in annotation_timestamps:
            del annotation_timestamps[task_id]
        print(f"Cleaned up expired annotation task: {task_id}")

    if expired_tasks:
        gc.collect()  # Force garbage collection after cleanup

    return len(expired_tasks)

def filter_dataframe_efficient(df, search_filter='', show_empty=False):
    """
    Memory-efficient filtering that avoids full DataFrame copies.
    Returns a filtered view/index instead of a full copy.
    """
    # Start with all indices
    mask = pd.Series([True] * len(df), index=df.index)

    # Filter out rows without Abstract text unless show_empty is True
    if not show_empty and 'Abstract' in df.columns:
        mask = mask & (df['Abstract'].notna()) & (df['Abstract'] != '')

    # Apply search filter
    matched_keywords = pd.Series([''] * len(df), index=df.index)

    if search_filter:
        search_terms = [term.strip() for term in search_filter.split(';') if term.strip()]
        search_mask = pd.Series([False] * len(df), index=df.index)

        for term in search_terms:
            term_mask = df.apply(lambda row: row.astype(str).str.contains(term, case=False).any(), axis=1)
            search_mask = search_mask | term_mask

            # Track matched keywords
            for idx in df[term_mask].index:
                if matched_keywords[idx]:
                    matched_keywords[idx] += '; ' + term
                else:
                    matched_keywords[idx] = term

        mask = mask & search_mask

    return mask, matched_keywords

def get_openai_response(api_key, model, abstract_text, question, dry_run=False):
    """Get response from OpenAI API or generate mock response for dry run"""
    if dry_run:
        # Generate random responses for dry run
        responses = [
            "Yes, this abstract mentions the treatment.",
            "No, this is not mentioned in the abstract.",
            "Partially relevant - see details in abstract.",
            "Not applicable to this study.",
            "Further investigation needed."
        ]
        time.sleep(0.1)  # Simulate API delay
        return random.choice(responses)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        prompt = f"""Given the following abstract, please answer the question concisely.

Abstract:
{abstract_text}

Question: {question}

Answer:"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant analyzing medical abstracts. Provide concise, factual answers based only on the information in the abstract."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def process_abstracts_batch(task_id, abstracts_batch, api_key, model, question, dry_run, thread_id):
    """Process a batch of abstracts"""
    results = []
    
    for idx, (index, row) in enumerate(abstracts_batch):
        try:
            abstract_text = row.get('Abstract', '')
            if not abstract_text:
                answer = "No abstract available"
            else:
                answer = get_openai_response(api_key, model, abstract_text, question, dry_run)
            
            results.append({
                'index': index,
                'answer': answer
            })
            
            # Update progress
            with threading.Lock():
                annotation_progress[task_id]['completed'] += 1
                
        except Exception as e:
            results.append({
                'index': index,
                'answer': f"Error: {str(e)}"
            })
    
    return results

@app.route('/')
def index():
    """Render the main page"""
    # Get OpenAI API key from environment if available
    openai_api_key = os.environ.get('OPENAI_API_KEY', '')
    return render_template_string(HTML_TEMPLATE, openai_api_key=openai_api_key)

@app.route('/api/abstracts')
def get_abstracts():
    """Get paginated abstracts data with efficient filtering"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    search = request.args.get('search', '')
    show_empty = request.args.get('show_empty', 'false').lower() == 'true'

    # Cleanup old results periodically (every request is fine given low frequency)
    cleanup_old_results()

    # Use efficient filtering
    mask, matched_keywords = filter_dataframe_efficient(abstracts_df, search, show_empty)

    # Get filtered indices (avoid full copy)
    filtered_indices = abstracts_df.index[mask]
    total = len(filtered_indices)

    # Paginate using indices
    start = (page - 1) * per_page
    end = start + per_page
    page_indices = filtered_indices[start:end]

    # Only copy the data we need for this page
    page_df = abstracts_df.loc[page_indices].copy()

    # Add matched keywords if search was used
    if search:
        page_df['Matched Keywords'] = matched_keywords[page_indices]

    # Convert to dict for JSON response
    data = page_df.to_dict('records')

    response_data = {
        'data': data,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }

    # Include search terms if present
    if search:
        search_terms = [term.strip() for term in search.split(';') if term.strip()]
        response_data['search_terms'] = search_terms

    return jsonify(response_data)

@app.route('/api/annotate', methods=['POST'])
def annotate_abstracts():
    """Start annotation process with efficient filtering"""
    data = request.json
    api_key = data.get('api_key')
    model = data.get('model', 'gpt-3.5-turbo')
    question = data.get('question')
    num_threads = int(data.get('num_threads', 4))
    dry_run = data.get('dry_run', False)
    search_filter = data.get('search_filter', '')
    show_empty = data.get('show_empty', False)

    # Generate task ID
    task_id = hashlib.md5(f"{question}{datetime.now()}".encode()).hexdigest()

    # Use efficient filtering
    mask, matched_keywords = filter_dataframe_efficient(abstracts_df, search_filter, show_empty)

    # Get filtered indices
    filtered_indices = abstracts_df.index[mask]

    # Only copy the filtered data we need for annotation
    filtered_df = abstracts_df.loc[filtered_indices].copy()

    # Add matched keywords if search was used
    if search_filter:
        filtered_df['Matched Keywords'] = matched_keywords[filtered_indices]

    # Initialize progress tracking
    total_abstracts = len(filtered_df)
    annotation_progress[task_id] = {
        'total': total_abstracts,
        'completed': 0,
        'status': 'running',
        'question': question
    }

    # Track creation time for cleanup
    annotation_timestamps[task_id] = datetime.now()

    # Split abstracts into batches for threading
    abstracts_list = list(filtered_df.iterrows())
    batch_size = max(1, total_abstracts // num_threads) if total_abstracts > num_threads else 1
    batches = [abstracts_list[i:i + batch_size] for i in range(0, total_abstracts, batch_size)]

    # Process in background
    def run_annotation():
        all_results = []

        with ThreadPoolExecutor(max_workers=min(num_threads, len(batches))) as executor:
            futures = []
            for i, batch in enumerate(batches):
                future = executor.submit(
                    process_abstracts_batch,
                    task_id, batch, api_key, model, question, dry_run, i
                )
                futures.append(future)

            # Collect results
            for future in as_completed(futures):
                batch_results = future.result()
                all_results.extend(batch_results)

        # Update dataframe with results
        result_df = filtered_df.copy()
        answer_column = f"Answer: {question[:50]}..."

        # Create answer mapping
        answer_map = {r['index']: r['answer'] for r in all_results}

        # Add the answer column
        result_df[answer_column] = result_df.index.map(lambda x: answer_map.get(x, 'No answer'))

        # Ensure all columns are preserved
        print(f"Result columns after annotation: {list(result_df.columns)}")

        # Store results
        annotation_results[task_id] = result_df
        annotation_progress[task_id]['status'] = 'completed'

        # Clean up temporary variables and force garbage collection
        del all_results
        del answer_map
        gc.collect()

    # Start annotation in background thread
    thread = threading.Thread(target=run_annotation)
    thread.start()

    return jsonify({'task_id': task_id, 'total': total_abstracts})

@app.route('/api/progress/<task_id>')
def get_progress(task_id):
    """Get annotation progress"""
    if task_id not in annotation_progress:
        return jsonify({'error': 'Task not found'}), 404
    
    progress = annotation_progress[task_id]
    return jsonify(progress)

@app.route('/api/annotated/<task_id>')
def get_annotated_results(task_id):
    """Get annotated results for display in table"""
    if task_id not in annotation_results:
        return jsonify({'error': 'Results not found'}), 404
    
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    result_df = annotation_results[task_id]
    
    # Paginate
    total = len(result_df)
    start = (page - 1) * per_page
    end = start + per_page
    
    # Convert to dict for JSON response
    data = result_df.iloc[start:end].to_dict('records')
    
    response_data = {
        'data': data,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page,
        'columns': list(result_df.columns)
    }
    
    # Check if search terms were used
    if 'Matched Keywords' in result_df.columns:
        response_data['search_terms'] = True
    
    return jsonify(response_data)

@app.route('/api/download/current')
def download_current_view():
    """Download current filtered view as CSV with streaming"""
    search = request.args.get('search', '')
    show_empty = request.args.get('show_empty', 'false').lower() == 'true'

    # Use efficient filtering
    mask, matched_keywords = filter_dataframe_efficient(abstracts_df, search, show_empty)

    # Get filtered indices (avoid full copy)
    filtered_indices = abstracts_df.index[mask]

    # Reorder columns to match display
    cols = ['Abstract #', 'Track', 'First Author', 'Abstract title', 'Abstract']
    if search:
        cols.append('Matched Keywords')

    # Select only existing columns
    existing_cols = [col for col in cols if col in abstracts_df.columns]

    # Create CSV with streaming to avoid loading everything in memory
    output = io.StringIO()

    # Write header
    output.write(','.join(existing_cols) + '\n')

    # Write data in chunks to minimize memory usage
    chunk_size = 1000
    for i in range(0, len(filtered_indices), chunk_size):
        chunk_indices = filtered_indices[i:i + chunk_size]
        chunk_df = abstracts_df.loc[chunk_indices, existing_cols].copy()

        # Add matched keywords if search was used
        if search:
            chunk_df['Matched Keywords'] = matched_keywords[chunk_indices]

        # Write chunk to CSV (without header)
        chunk_df.to_csv(output, index=False, header=False, encoding='utf-8')

        # Clear chunk from memory
        del chunk_df

    output.seek(0)

    # Convert to bytes
    output_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
    output_bytes.seek(0)

    filename = f"esmo_abstracts_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return send_file(
        output_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/download/<task_id>')
def download_results(task_id):
    """Download annotated results as CSV with streaming"""
    if task_id not in annotation_results:
        return jsonify({'error': 'Results not found'}), 404

    result_df = annotation_results[task_id]

    # Reorder columns to match display
    base_cols = ['Abstract #', 'Track', 'First Author', 'Abstract title', 'Abstract']

    # Add matched keywords if present
    if 'Matched Keywords' in result_df.columns:
        base_cols.append('Matched Keywords')

    # Add annotation columns
    annotation_cols = [col for col in result_df.columns if col.startswith('Answer:')]
    all_cols = base_cols + annotation_cols

    # Select only existing columns in the correct order
    existing_cols = [col for col in all_cols if col in result_df.columns]

    # Create CSV with streaming to avoid loading everything in memory
    output = io.StringIO()

    # Write header
    output.write(','.join(existing_cols) + '\n')

    # Write data in chunks to minimize memory usage
    chunk_size = 1000
    for i in range(0, len(result_df), chunk_size):
        chunk_df = result_df.iloc[i:i + chunk_size][existing_cols].copy()
        chunk_df.to_csv(output, index=False, header=False, encoding='utf-8')
        del chunk_df

    output.seek(0)

    # Convert to bytes
    output_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
    output_bytes.seek(0)

    filename = f"annotated_abstracts_{task_id[:8]}.csv"

    return send_file(
        output_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/models')
def get_models():
    """Get available OpenAI models"""
    return jsonify({
        'models': [
            {'id': 'gpt-5-nano', 'name': 'GPT-5 Nano - Most cost-effective (default)'},
            {'id': 'gpt-5-mini', 'name': 'GPT-5 Mini - Fast and affordable'},
            {'id': 'gpt-5', 'name': 'GPT-5 - Smartest, fastest model with thinking built in'},
            {'id': 'o4-mini', 'name': 'o4-mini - Fast reasoning for math, coding, visual tasks'},
            {'id': 'o3', 'name': 'o3 - Most powerful reasoning model'},
            {'id': 'o1', 'name': 'o1 - Advanced reasoning model'},
            {'id': 'o1-mini', 'name': 'o1-mini - Faster, affordable reasoning'},
            {'id': 'gpt-4o', 'name': 'GPT-4o - Multimodal text and images'},
            {'id': 'gpt-4o-mini', 'name': 'GPT-4o mini - Fast, affordable small model'},
            {'id': 'gpt-4-turbo', 'name': 'GPT-4 Turbo'},
            {'id': 'gpt-4', 'name': 'GPT-4'}
        ]
    })

@app.route('/api/stats')
def get_stats():
    """Get statistics about the loaded data"""
    total = len(abstracts_df)
    
    # Count abstracts with text
    if 'Abstract' in abstracts_df.columns:
        with_abstracts = len(abstracts_df[abstracts_df['Abstract'].notna() & (abstracts_df['Abstract'] != '')])
    else:
        with_abstracts = 0
    
    return jsonify({
        'total_abstracts': with_abstracts,  # Show only abstracts with content by default
        'abstracts_with_text': with_abstracts,
        'total_all': total,  # Total including empty ones
        'columns': list(abstracts_df.columns)
    })

if __name__ == '__main__':
    # Get host and port from environment variables with defaults
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))

    # Get debug mode from environment (default to False for production)
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    print("\n" + "="*50)
    print("ESMO 2025 Abstract Annotator")
    print("="*50)
    print("\nStarting web server...")
    print(f"Mode: {'Development (Debug)' if debug else 'Production'}")
    print(f"Open your browser and go to: http://{host}:{port}")
    if not debug:
        print("\nWARNING: Using Flask's built-in server in production is not recommended.")
        print("For production, use: gunicorn -w 4 -b 0.0.0.0:5000 conference-webapp:app")
    print("\nPress CTRL+C to stop the server\n")

    # Run with configured host and port
    app.run(debug=debug, host=host, port=port)