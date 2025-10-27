using System;
using Microsoft.Office.Tools;
using Word = Microsoft.Office.Interop.Word;
using Office = Microsoft.Office.Core;

namespace WordMarkdownAddIn
{
	public partial class ThisAddIn
	{
		public static CustomTaskPane MarkdownPane { get; private set; }
		public static Controls.TaskPaneControl PaneControl { get; private set; }

		private void ThisAddIn_Startup(object sender, EventArgs e)
		{
			PaneControl = new Controls.TaskPaneControl();
			MarkdownPane = this.CustomTaskPanes.Add(PaneControl, "Markdown");
			MarkdownPane.Visible = true;

			// Load markdown from the document if present
			try
			{
				var md = Services.DocumentSyncService.LoadMarkdownFromActiveDocument(Application);
				if (!string.IsNullOrEmpty(md))
				{
					PaneControl.SetMarkdown(md);
				}
			}
			catch { /* ignore at startup */ }

			// Track Word save to persist current Markdown into CustomXMLPart
			try
			{
				this.Application.DocumentBeforeSave += Application_DocumentBeforeSave;
			}
			catch { }
		}

		private void ThisAddIn_Shutdown(object sender, EventArgs e)
		{
			try { this.Application.DocumentBeforeSave -= Application_DocumentBeforeSave; } catch { }
		}

		private void Application_DocumentBeforeSave(Word.Document Doc, ref bool SaveAsUI, ref bool Cancel)
		{
			try
			{
				var md = PaneControl?.GetCachedMarkdown() ?? string.Empty;
				Services.DocumentSyncService.SaveMarkdownToActiveDocument(Application, md);
			}
			catch { }
		}

		protected override Office.IRibbonExtensibility CreateRibbonExtensibilityObject()
		{
			return new MarkdownRibbon();
		}

		public void TogglePane()
		{
			if (MarkdownPane != null)
			{
				MarkdownPane.Visible = !MarkdownPane.Visible;
			}
		}
	}
}