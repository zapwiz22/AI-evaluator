import React from 'react';
import FileUpload from '../components/FileUpload';

const Dashboard = () => {
	return (
		<main className="page-shell">
			<header className="hero-card">
				<p className="eyebrow">AI Evaluator</p>
				<h1>Upload Reports, Get Briefs, Tables, Flowcharts, and Authenticity Metrics</h1>
				<p className="hero-copy">
					This dashboard analyzes uploaded report PDFs, generates a concise summary,
					extracts structured table data, builds a Mermaid flowchart,
					estimates plagiarism and AI-generated likelihood,
					and verifies factual claims through API-ready endpoints.
				</p>
			</header>

			<section className="content-card">
				<FileUpload />
			</section>

			<section className="api-card">
				<h2>Verification API</h2>
				<p>
					External clients can call <code>POST /api/verify-claims</code> with a list of claims.
				</p>
				<pre>
{`{
	"claims": [
		"Revenue increased by 20% in 2025",
		"The policy was enacted in 2019"
	],
	"search_context": "Optional external evidence text"
}`}
				</pre>
			</section>
		</main>
	);
};

export default Dashboard;
