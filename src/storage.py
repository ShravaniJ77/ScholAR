"""Local storage manager for ScholAR research data."""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import shutil

class ResearchStorage:
    """Manages local storage of research results."""

    def __init__(self, storage_dir: str = "scholarpython_research"):
        """Initialize storage directory and database."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        # Create data subdirectories
        self.data_dir = self.storage_dir / "data"
        self.data_dir.mkdir(exist_ok=True)

        self.db_path = self.storage_dir / "research_history.db"
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for search history."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                papers_count INTEGER,
                contradictions_count INTEGER,
                file_path TEXT,
                status TEXT DEFAULT 'completed'
            )
        """)

        conn.commit()
        conn.close()

    def save_research(self, topic: str, research_data: dict) -> str:
        """
        Save research results locally.

        Args:
            topic: Research topic
            research_data: Complete research data (papers, contradictions, report, etc.)

        Returns:
            File path where data was saved
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_safe = "".join(c for c in topic if c.isalnum() or c in (' ', '_')).rstrip()[:50]
        folder_name = f"{topic_safe}_{timestamp}"
        research_folder = self.data_dir / folder_name

        research_folder.mkdir(exist_ok=True)

        # Save research data as JSON
        research_file = research_folder / "research_data.json"
        with open(research_file, 'w', encoding='utf-8') as f:
            json.dump(research_data, f, indent=2, ensure_ascii=False)

        # Save metadata
        metadata = {
            "topic": topic,
            "timestamp": timestamp,
            "papers_count": len(research_data.get('papers', [])),
            "contradictions_count": len(research_data.get('contradictions', [])),
            "report_length": len(research_data.get('report', ''))
        }
        metadata_file = research_folder / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        # Save report as markdown
        report_file = research_folder / f"{topic_safe}_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(research_data.get('report', 'No report generated'))

        # Save papers list as CSV
        papers_file = research_folder / "papers.csv"
        if research_data.get('papers'):
            import csv
            with open(papers_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['title', 'year', 'authors', 'citations', 'abstract'])
                writer.writeheader()
                for paper in research_data.get('papers', []):
                    writer.writerow({
                        'title': paper.get('title', ''),
                        'year': paper.get('year', ''),
                        'authors': paper.get('author_str', ''),
                        'citations': paper.get('citationCount', 0),
                        'abstract': paper.get('abstract', '')[:200]
                    })

        # Save contradictions as JSON
        contradictions_file = research_folder / "contradictions.json"
        with open(contradictions_file, 'w', encoding='utf-8') as f:
            json.dump(research_data.get('contradictions', []), f, indent=2, ensure_ascii=False)

        # Update database
        self._add_to_history(topic, timestamp, metadata, str(research_folder))

        return str(research_folder)

    def _add_to_history(self, topic: str, timestamp: str, metadata: dict, file_path: str):
        """Add research to history database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO research_history
            (topic, timestamp, papers_count, contradictions_count, file_path, status)
            VALUES (?, ?, ?, ?, ?, 'completed')
        """, (
            topic,
            timestamp,
            metadata.get('papers_count', 0),
            metadata.get('contradictions_count', 0),
            file_path
        ))

        conn.commit()
        conn.close()

    def get_history(self, limit: int = 50) -> list:
        """Get research history (most recent first)."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, topic, timestamp, papers_count, contradictions_count, file_path, status
            FROM research_history
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'topic': row[1],
                'timestamp': row[2],
                'papers_count': row[3],
                'contradictions_count': row[4],
                'file_path': row[5],
                'status': row[6]
            })

        conn.close()
        return results

    def load_research(self, research_path: str) -> dict:
        """Load a saved research result."""
        research_file = Path(research_path) / "research_data.json"

        if not research_file.exists():
            return None

        with open(research_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_storage_size(self) -> str:
        """Get total size of stored research."""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.data_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)

        # Convert to MB
        mb = total_size / (1024 * 1024)
        return f"{mb:.2f} MB"

    def delete_research(self, research_path: str):
        """Delete a saved research result."""
        research_folder = Path(research_path)
        if research_folder.exists():
            shutil.rmtree(research_folder)

            # Remove from database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("DELETE FROM research_history WHERE file_path = ?", (research_path,))
            conn.commit()
            conn.close()

    def export_research(self, research_path: str, export_format: str = "zip"):
        """Export research in various formats."""
        research_folder = Path(research_path)

        if export_format == "zip":
            export_file = research_folder.parent / f"{research_folder.name}.zip"
            shutil.make_archive(str(export_file.with_suffix('')), 'zip', research_folder.parent, research_folder.name)
            return str(export_file)

        return None

    def get_all_research_files(self) -> list:
        """Get list of all files in a research folder."""
        all_files = []
        for folder in sorted(self.data_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if folder.is_dir():
                files = {
                    'name': folder.name,
                    'path': str(folder),
                    'created': datetime.fromtimestamp(folder.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    'files': []
                }

                for file in folder.glob('*'):
                    if file.is_file():
                        size_kb = file.stat().st_size / 1024
                        files['files'].append({
                            'name': file.name,
                            'size': f"{size_kb:.2f} KB"
                        })

                all_files.append(files)

        return all_files
