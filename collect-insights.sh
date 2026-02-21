#!/bin/bash
# Claude Code Insights データ収集スクリプト
# 各PCで実行してください

OUTPUT_DIR="$HOME/claude-insights-export"
HOSTNAME=$(hostname | sed 's/\.local$//')
TIMESTAMP=$(date +%Y%m%d)
ARCHIVE_NAME="insights-${HOSTNAME}-${TIMESTAMP}.tar.gz"

echo "=== Claude Code Insights データ収集 ==="
echo "PC名: $HOSTNAME"
echo ""

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/facets"
mkdir -p "$OUTPUT_DIR/sessions"

# facets収集
FACETS_DIR="$HOME/.claude/usage-data/facets"
if [ -d "$FACETS_DIR" ]; then
    cp "$FACETS_DIR"/*.json "$OUTPUT_DIR/facets/" 2>/dev/null
    FACET_COUNT=$(ls "$OUTPUT_DIR/facets/"*.json 2>/dev/null | wc -l | tr -d ' ')
    echo "facets: ${FACET_COUNT}件"
else
    echo "facets: なし（/insightsを先に実行してください）"
fi

# sessions-index収集
FOUND_SESSIONS=0
for idx in "$HOME/.claude/projects"/*/sessions-index.json; do
    if [ -f "$idx" ]; then
        PROJECT_DIR=$(dirname "$idx")
        PROJECT_NAME=$(basename "$PROJECT_DIR")
        cp "$idx" "$OUTPUT_DIR/sessions/${PROJECT_NAME}_sessions-index.json"
        FOUND_SESSIONS=$((FOUND_SESSIONS + 1))
    fi
done
echo "sessions-index: ${FOUND_SESSIONS}件"

# PC情報
cat > "$OUTPUT_DIR/pc-info.json" << PCEOF
{
    "hostname": "$HOSTNAME",
    "os": "$(uname -s)",
    "os_version": "$(uname -r)",
    "arch": "$(uname -m)",
    "collected_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "claude_code_version": "$(claude --version 2>/dev/null || echo 'unknown')"
}
PCEOF
echo "PC情報: 保存済み"

# HTMLレポートも含める（参照用）
if [ -f "$HOME/.claude/usage-data/report.html" ]; then
    cp "$HOME/.claude/usage-data/report.html" "$OUTPUT_DIR/report-${HOSTNAME}.html"
    echo "HTMLレポート: コピー済み"
fi

# アーカイブ作成
cd "$HOME"
tar czf "$ARCHIVE_NAME" -C "$OUTPUT_DIR" .
echo ""
echo "=== 完了 ==="
echo "ファイル: $HOME/$ARCHIVE_NAME"
echo "サイズ: $(du -h "$HOME/$ARCHIVE_NAME" | cut -f1)"
echo ""
echo "このファイルを統合用のMacに転送してください。"
