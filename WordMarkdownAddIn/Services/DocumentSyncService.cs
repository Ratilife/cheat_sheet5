using System;
using Word = Microsoft.Office.Interop.Word;
using Office = Microsoft.Office.Core;

namespace WordMarkdownAddIn.Services
{
	public static class DocumentSyncService
	{
		public const string NamespaceUri = "urn:markdown/source";

		public static string LoadMarkdownFromActiveDocument(Word.Application app)
		{
			if (app == null || app.ActiveDocument == null) return null;
			var doc = app.ActiveDocument;
			Office.CustomXMLPart part = FindExistingPart(doc);
			if (part == null) return null;
			try
			{
				var node = part.SelectSingleNode("/*[local-name()='markdown']/*[local-name()='content']");
				if (node != null)
				{
					return node.Text;
				}
			}
			catch { }
			return null;
		}

		public static void SaveMarkdownToActiveDocument(Word.Application app, string markdown)
		{
			if (app == null || app.ActiveDocument == null) return;
			var doc = app.ActiveDocument;
			var existing = FindExistingPart(doc);
			if (existing != null)
			{
				existing.Delete();
			}
			var xml = BuildXml(markdown ?? string.Empty);
			doc.CustomXMLParts.Add(xml);
		}

		private static string BuildXml(string content)
		{
			// Wrap markdown in CDATA inside a namespaced root
			return "<md:markdown xmlns:md='" + NamespaceUri + "'>" +
				"<md:content><![CDATA[" + content + "]]></md:content>" +
				"</md:markdown>";
		}

		private static Office.CustomXMLPart FindExistingPart(Word.Document doc)
		{
			try
			{
				Office.CustomXMLParts parts = doc.CustomXMLParts;
				foreach (Office.CustomXMLPart p in parts)
				{
					try
					{
						var root = p.DocumentElement;
						if (root != null && string.Equals(root.NamespaceURI, NamespaceUri, StringComparison.OrdinalIgnoreCase))
						{
							return p;
						}
					}
					catch { }
				}
			}
			catch { }
			return null;
		}
	}
}