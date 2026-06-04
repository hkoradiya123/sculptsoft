from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
	HRFlowable,
	ListFlowable,
	ListItem,
	PageBreak,
	Paragraph,
	Preformatted,
	SimpleDocTemplate,
	Spacer,
	Table,
	TableStyle,
)


OUTPUT_FILE = Path(__file__).with_name("voice-agent-architecture-whitepaper.pdf")


def build_styles():
	styles = getSampleStyleSheet()
	styles.add(
		ParagraphStyle(
			name="CoverTitle",
			parent=styles["Title"],
			fontName="Helvetica-Bold",
			fontSize=24,
			leading=29,
			alignment=TA_CENTER,
			textColor=colors.HexColor("#102a43"),
			spaceAfter=14,
		)
	)
	styles.add(
		ParagraphStyle(
			name="CoverSubtitle",
			parent=styles["BodyText"],
			fontName="Helvetica",
			fontSize=11,
			leading=14,
			alignment=TA_CENTER,
			textColor=colors.HexColor("#486581"),
			spaceAfter=8,
		)
	)
	styles.add(
		ParagraphStyle(
			name="SectionHeader",
			parent=styles["Heading1"],
			fontName="Helvetica-Bold",
			fontSize=15,
			leading=19,
			textColor=colors.HexColor("#102a43"),
			spaceBefore=10,
			spaceAfter=8,
		)
	)
	styles.add(
		ParagraphStyle(
			name="SubHeader",
			parent=styles["Heading2"],
			fontName="Helvetica-Bold",
			fontSize=11.5,
			leading=14,
			textColor=colors.HexColor("#243b53"),
			spaceBefore=8,
			spaceAfter=4,
		)
	)
	styles.add(
		ParagraphStyle(
			name="Body",
			parent=styles["BodyText"],
			fontName="Helvetica",
			fontSize=9.5,
			leading=13,
			textColor=colors.HexColor("#243b53"),
			spaceAfter=6,
		)
	)
	styles.add(
		ParagraphStyle(
			name="Note",
			parent=styles["BodyText"],
			fontName="Helvetica-Oblique",
			fontSize=9,
			leading=12,
			textColor=colors.HexColor("#627d98"),
			leftIndent=10,
			spaceBefore=2,
			spaceAfter=6,
		)
	)
	styles.add(
		ParagraphStyle(
			name="CodeBlock",
			parent=styles["Code"],
			fontName="Courier",
			fontSize=8.5,
			leading=11,
			textColor=colors.HexColor("#102a43"),
			backColor=colors.HexColor("#f0f4f8"),
			borderColor=colors.HexColor("#d9e2ec"),
			borderWidth=0.5,
			borderPadding=7,
			spaceBefore=4,
			spaceAfter=8,
		)
	)
	return styles


def paragraph(text, style):
	return Paragraph(text, style)


def bullet_list(items, styles):
	return ListFlowable(
		[ListItem(Paragraph(item, styles["Body"])) for item in items],
		bulletType="bullet",
		leftIndent=16,
	)


def code_block(text, styles):
	return Preformatted(text, styles["CodeBlock"])


def metric_table(rows):
	table = Table(rows, colWidths=[110, 110, 270])
	table.setStyle(
		TableStyle(
			[
				("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102a43")),
				("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
				("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
				("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
				("FONTSIZE", (0, 0), (-1, -1), 9),
				("LEADING", (0, 0), (-1, -1), 11),
				("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
				("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.HexColor("#edf2f7")]),
				("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#bcccdc")),
				("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
				("LEFTPADDING", (0, 0), (-1, -1), 8),
				("RIGHTPADDING", (0, 0), (-1, -1), 8),
				("TOPPADDING", (0, 0), (-1, -1), 6),
				("BOTTOMPADDING", (0, 0), (-1, -1), 6),
			]
		)
	)
	return table


def build_story(styles):
	story = []

	story.append(Spacer(1, 1.2 * mm * 25.4 / 1))
	story.append(paragraph("Voice Agent Architecture Whitepaper", styles["CoverTitle"]))
	story.append(paragraph("A technical architecture guide for realtime customer support systems, voice assistants, and tool-using agents.", styles["CoverSubtitle"]))
	story.append(paragraph("Prepared from the uploaded draft and expanded into a startup-style engineering document.", styles["CoverSubtitle"]))
	story.append(Spacer(1, 0.4 * 72))
	story.append(HRFlowable(width="70%", color=colors.HexColor("#d9e2ec"), thickness=1))
	story.append(Spacer(1, 0.25 * 72))
	story.append(paragraph("This document extends the original architecture overview with the highest-value sections for production voice systems: call lifecycle, latency budgets, VAD, agent state machines, prompt architecture, escalation paths, and enterprise-grade platform concerns.", styles["Body"]))
	story.append(Spacer(1, 0.35 * 72))

	story.append(paragraph("Executive Summary", styles["SectionHeader"]))
	story.append(paragraph(
		"Voice agents are constrained by latency, state management, prompt composition, and operational reliability. A production system must coordinate speech input, real-time inference, tool execution, retrieval, escalation, and response synthesis while preserving turn-taking behavior and predictable costs.",
		styles["Body"],
	))
	story.append(paragraph(
		"The architecture below treats the voice assistant as a stateful platform rather than a single model call. That framing makes the system easier to reason about, debug, benchmark, and scale.",
		styles["Body"],
	))

	story.append(paragraph("1. Detailed Call Lifecycle", styles["SectionHeader"]))
	story.append(paragraph(
		"The runtime flow should be explicit so engineers can map each user turn to the correct subsystem. This is the control path most teams need when diagnosing barge-in behavior, tool-call delays, or missed responses.",
		styles["Body"],
	))
	story.append(code_block(
		"Incoming Call\n    ↓\nCall Authentication\n    ↓\nVoice Activity Detection\n    ↓\nASR Processing\n    ↓\nIntent Detection\n    ↓\nContext Retrieval\n    ↓\nTool Selection\n    ↓\nBusiness Action\n    ↓\nResponse Generation\n    ↓\nTTS\n    ↓\nCall End",
		styles,
	))
	story.append(bullet_list([
		"Call authentication should confirm tenant, caller identity, and policy scope before the model starts acting.",
		"VAD gates the rest of the pipeline so the system does not pay the ASR and LLM cost during silence.",
		"Tool selection should be separated from response generation so the agent can decide whether to act, ask a question, or escalate.",
	], styles))

	story.append(paragraph("2. Latency Breakdown", styles["SectionHeader"]))
	story.append(paragraph(
		"Voice products succeed or fail on perceived responsiveness. The latency budget below is a practical target for conversational quality; every stage should report its measured p50 and p95 timings.",
		styles["Body"],
	))
	story.append(metric_table([
		["Component", "Target", "Notes"],
		["ASR", "100 ms", "Streaming transcription should start producing partial text quickly."],
		["LLM", "200 ms", "Keep the prompt small and use the minimum necessary context."],
		["Tool Calls", "100 ms", "Prefer cached, indexed, or pre-fetched lookups for common paths."],
		["TTS", "150 ms", "Start synthesis before the whole response is finalized when possible."],
		["Network", "100 ms", "WebSocket and edge placement matter in live call scenarios."],
		["Total", "< 700 ms", "A good conversational target for realtime voice startups."],
	]))

	story.append(paragraph("3. Voice Activity Detection", styles["SectionHeader"]))
	story.append(paragraph(
		"VAD is the gatekeeper for turn-taking. It prevents false starts, supports barge-in, and allows the platform to decide when to transcribe and when to stay idle.",
		styles["Body"],
	))
	story.append(code_block(
		"Customer speaking?\n      ↓\nVAD detects speech\n      ↓\nStart processing",
		styles,
	))
	story.append(bullet_list([
		"Silero VAD is a strong default for low-latency speech detection in application code.",
		"WebRTC VAD is lightweight and often used where CPU budget is tight.",
		"Deepgram endpointing can be useful when the transcription stack and endpointing policy need to be aligned.",
	], styles))
	story.append(paragraph("For barge-in systems, the VAD layer should be paired with audio interruption rules so a new customer utterance can cut off the current TTS response cleanly.", styles["Body"]))

	story.append(paragraph("4. Agent State Machine", styles["SectionHeader"]))
	story.append(paragraph(
		"A small state machine makes production behavior understandable. It also creates a common language for logs, traces, retries, and QA playback.",
		styles["Body"],
	))
	story.append(code_block(
		"IDLE\n ↓\nLISTENING\n ↓\nTHINKING\n ↓\nTOOL_EXECUTION\n ↓\nRESPONDING\n ↓\nLISTENING",
		styles,
	))
	story.append(bullet_list([
		"Transitions should be emitted into telemetry so every turn can be replayed later.",
		"Tool execution should be a dedicated state, not just an inline function call.",
		"The system should return to LISTENING after a response so turn-taking stays explicit.",
	], styles))

	story.append(paragraph("5. Prompt Engineering Layer", styles["SectionHeader"]))
	story.append(paragraph(
		"At scale, prompt architecture becomes a platform concern. Separate the static policy prompt from runtime context, and keep tool definitions structured so they can be versioned independently.",
		styles["Body"],
	))
	story.append(paragraph("System Prompt", styles["SubHeader"]))
	story.append(code_block("You are a customer support agent.", styles))
	story.append(paragraph("Dynamic Prompt", styles["SubHeader"]))
	story.append(code_block("Customer Name\nOrder History\nCurrent Context", styles))
	story.append(paragraph("Tool Definitions", styles["SubHeader"]))
	story.append(code_block('{\n  "name": "check_order"\n}', styles))
	story.append(paragraph(
		"The main design rule is to keep policy, state, and factual context separate so prompt changes do not destabilize behavior.",
		styles["Body"],
	))

	story.append(paragraph("6. AI Agent Builder Architecture", styles["SectionHeader"]))
	story.append(paragraph(
		"A commercial agent platform is a composition system. The platform must let builders attach prompts, voice, knowledge, tools, policies, and escalation rules without rewriting the runtime.",
		styles["Body"],
	))
	story.append(code_block(
		"Agent\n ├── Prompt\n ├── Voice\n ├── Knowledge Base\n ├── Tools\n ├── Policies\n └── Escalation Rules",
		styles,
	))
	story.append(bullet_list([
		"This is the product shape used by voice-first platforms such as Vapi, Retell, and Bland.",
		"The builder should store artifacts versioned by tenant and environment.",
		"Runtime policy evaluation should happen before a risky action or escalation.",
	], styles))

	story.append(paragraph("7. Human Escalation System", styles["SectionHeader"]))
	story.append(paragraph(
		"Enterprise voice systems need a clear path from autonomous handling to human takeover. Escalation should be driven by sentiment, confidence, policy violations, and resolution thresholds.",
		styles["Body"]
	))
	story.append(code_block(
		"Customer angry\n      ↓\nSentiment score\n      ↓\nEscalate to human agent\n      ↓\nTransfer context and transcript",
		styles,
	))
	story.append(bullet_list([
		"Preserve transcript, intent, and tool history so the human agent does not start cold.",
		"Escalation should be auditable and policy-driven rather than ad hoc.",
		"A handoff should also freeze the agent state to prevent duplicate actions.",
	], styles))

	story.append(PageBreak())
	story.append(paragraph("8. Deployment Architecture", styles["SectionHeader"]))
	story.append(paragraph(
		"The deployment layout should separate realtime media handling, orchestration, storage, and analytics. That separation keeps low-latency paths short and lets batch systems scale independently.",
		styles["Body"]
	))
	story.append(bullet_list([
		"Realtime media service for WebSocket audio ingress and egress.",
		"Orchestration service for prompts, routing, tool selection, and policy checks.",
		"Storage layer for transcripts, call summaries, and audit records.",
		"Analytics pipeline for quality, latency, and cost tracking.",
	], styles))

	story.append(paragraph("9. Knowledge Base Ingestion Pipeline", styles["SectionHeader"]))
	story.append(paragraph(
		"Retrieval quality matters as much as model quality. A strong ingestion pipeline converts documents into searchable, chunked, and permission-scoped context that can be injected into the prompt only when needed.",
		styles["Body"]
	))
	story.append(code_block(
		"Docs / PDFs / FAQs / Tickets\n        ↓\nChunking + Cleaning\n        ↓\nEmbedding + Indexing\n        ↓\nPermission Filtering\n        ↓\nRetrieval at Turn Time",
		styles,
	))
	story.append(bullet_list([
		"Store chunk provenance so the assistant can cite where an answer came from.",
		"Apply tenant and role filters before retrieval results reach the model.",
		"Refresh high-priority documents often enough to avoid stale answers.",
	], styles))

	story.append(paragraph("10. Multi-Tenant SaaS Design", styles["SectionHeader"]))
	story.append(paragraph(
		"A voice agent platform quickly becomes multi-tenant. Tenancy should be enforced in storage, prompt assembly, tool access, analytics, and billing so customers remain isolated by design.",
		styles["Body"]
	))
	story.append(bullet_list([
		"Tenant-specific prompts and voice settings should be stored separately from shared infrastructure settings.",
		"Usage counters must be attributable per tenant and per agent.",
		"Administrative operations should carry explicit tenant context in every API call.",
	], styles))

	story.append(paragraph("11. Billing Architecture", styles["SectionHeader"]))
	story.append(paragraph(
		"Billing in voice systems is usually a combination of minute-based usage, ASR/TTS costs, LLM token costs, and premium feature fees. The platform should compute usage from immutable events rather than mutable dashboards.",
		styles["Body"]
	))
	story.append(metric_table([
		["Billable Unit", "Source", "Example"],
		["Call Minutes", "Call session events", "12.4 minutes handled"],
		["ASR Usage", "Transcription events", "37,000 audio frames processed"],
		["LLM Tokens", "Prompt and response logs", "18k input / 4k output tokens"],
		["Escalations", "Handoff events", "3 human transfers"],
	]))

	story.append(paragraph("12. Security Deep Dive", styles["SectionHeader"]))
	story.append(paragraph(
		"Security is not only authentication. Voice systems need tenant isolation, PII handling, prompt-injection defenses, tool authorization, and audit logging for every action that could affect a customer account.",
		styles["Body"]
	))
	story.append(bullet_list([
		"Authenticate the caller and validate the tenant before loading sensitive context.",
		"Sanitize external text before it is placed into prompt context or tool parameters.",
		"Use allowlisted tools with per-tool policy checks.",
		"Log all customer-impacting operations with trace IDs and actor context.",
	], styles))

	story.append(paragraph("13. Competitive Analysis", styles["SectionHeader"]))
	story.append(paragraph(
		"The ecosystem can be grouped by platform emphasis. The architectural tradeoffs below help buyers compare voice-first services quickly.",
		styles["Body"]
	))
	story.append(metric_table([
		["Platform", "Strength", "Typical Positioning"],
		["Vapi", "Developer-first", "Fast iteration and flexible integrations"],
		["Retell", "Voice quality", "Conversation handling and production workflows"],
		["Bland", "Outbound calling", "Sales and outreach automation"],
		["OpenAI Realtime", "Intelligence", "Low-latency multimodal agent building"],
		["Deepgram", "Speech stack", "ASR, endpointing, and voice infrastructure"],
	]))

	story.append(paragraph("14. System Design Interview Section", styles["SectionHeader"]))
	story.append(paragraph(
		"This document also works as an interview prep artifact. A strong systems answer should show how the platform handles realtime media, state, scale, and failure modes.",
		styles["Body"]
	))
	story.append(bullet_list([
		"Scaling WebSockets for many live conversations.",
		"Real-time audio processing and buffering.",
		"Distributed queues for async work and retries.",
		"Failover strategies for ASR, LLM, and TTS providers.",
		"Cost optimization across inference and telephony.",
	], styles))

	story.append(paragraph("Key Takeaway", styles["SectionHeader"]))
	story.append(paragraph(
		"The highest-impact additions are the ones that make the system operationally legible: call lifecycle, latency budget, VAD, agent state machine, prompt architecture, escalation, deployment boundaries, retrieval pipeline, tenancy, billing, security, and competitive positioning.",
		styles["Body"]
	))
	story.append(paragraph(
		"Taken together, those sections elevate the document from an overview into a whitepaper that reads like a real startup engineering artifact.",
		styles["Body"]
	))

	return story


def add_page_number(canvas, doc):
	canvas.saveState()
	width, height = A4
	canvas.setFont("Helvetica", 8)
	canvas.setFillColor(colors.HexColor("#627d98"))
	canvas.drawString(18 * mm, 12 * mm, "Voice Agent Architecture Whitepaper")
	canvas.drawRightString(width - 18 * mm, 12 * mm, f"Page {canvas.getPageNumber()}")
	canvas.restoreState()


def main():
	styles = build_styles()
	doc = SimpleDocTemplate(
		str(OUTPUT_FILE),
		pagesize=A4,
		rightMargin=18 * mm,
		leftMargin=18 * mm,
		topMargin=18 * mm,
		bottomMargin=18 * mm,
		title="Voice Agent Architecture Whitepaper",
		author="GitHub Copilot",
		subject="Professional architecture PDF for a voice agent system",
		creator="ReportLab",
	)
	story = build_story(styles)
	doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
	print(f"Created {OUTPUT_FILE}")


if __name__ == "__main__":
	main()
