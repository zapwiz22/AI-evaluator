import React from 'react';

const SummaryCard = ({ evaluation }) => {
	if (!evaluation) {
		return null;
	}

	const findings = Array.isArray(evaluation.key_findings) ? evaluation.key_findings : [];
	const tableColumns = evaluation.table_data?.columns || [];
	const tableRows = evaluation.table_data?.rows || [];

	return (
		<div style={{ background: '#ffffff', padding: '20px', borderRadius: '8px', border: '1px solid #dee2e6', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
			<h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '10px' }}>Document Brief</h3>
			<p style={{ lineHeight: '1.6', marginBottom: '16px' }}>{evaluation.summary || 'No summary available.'}</p>

			<h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '10px' }}>Key Findings</h3>
			<ul style={{ lineHeight: '1.6', paddingLeft: '20px', marginBottom: '16px' }}>
				{findings.map((finding, index) => (
					<li key={`${finding}-${index}`} style={{ marginBottom: '8px' }}>{finding}</li>
				))}
			</ul>

			{tableColumns.length > 0 && (
				<>
					<h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '10px' }}>Extracted Table</h3>
					<div style={{ overflowX: 'auto' }}>
						<table style={{ width: '100%', borderCollapse: 'collapse' }}>
							<thead>
								<tr>
									{tableColumns.map((column, idx) => (
										<th key={`${column}-${idx}`} style={{ textAlign: 'left', borderBottom: '1px solid #ddd', padding: '8px' }}>
											{column}
										</th>
									))}
								</tr>
							</thead>
							<tbody>
								{tableRows.map((row, rowIndex) => (
									<tr key={`row-${rowIndex}`}>
										{row.map((cell, cellIndex) => (
											<td key={`cell-${rowIndex}-${cellIndex}`} style={{ borderBottom: '1px solid #f2f2f2', padding: '8px' }}>
												{cell}
											</td>
										))}
									</tr>
								))}
							</tbody>
						</table>
					</div>
				</>
			)}
		</div>
	);
};

export default SummaryCard;
