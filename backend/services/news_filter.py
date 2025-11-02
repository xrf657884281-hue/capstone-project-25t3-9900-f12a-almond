"""
News quality filter for filtering news articles
"""
from typing import List, Dict


class NewsQualityFilter:
    """Filter news articles based on quality criteria"""

    def __init__(self):
        pass

    def filter_articles(self, articles: List[Dict], min_quality: float = 0.6) -> List[Dict]:
        """
        Filter articles based on quality score

        Args:
            articles: List of news articles
            min_quality: Minimum quality score (0-1)

        Returns:
            Filtered list of articles
        """
        filtered = []

        for article in articles:
            # Basic quality checks
            if self._check_article_quality(article, min_quality):
                filtered.append(article)

        return filtered

    def _check_article_quality(self, article: Dict, min_quality: float) -> bool:
        """
        Check if an article meets minimum quality standards

        Args:
            article: News article dict
            min_quality: Minimum quality threshold

        Returns:
            True if article passes quality check
        """
        score = 0.0
        checks = 0

        # Check if article has title
        if article.get('title') and len(article.get('title', '')) > 10:
            score += 1
            checks += 1
        else:
            checks += 1

        # Check if article has description
        if article.get('description') and len(article.get('description', '')) > 20:
            score += 1
            checks += 1
        else:
            checks += 1

        # Check if article has content
        if article.get('content') and len(article.get('content', '')) > 50:
            score += 1
            checks += 1
        else:
            checks += 1

        # Check if article has source
        if article.get('source') and article.get('source', {}).get('name'):
            score += 1
            checks += 1
        else:
            checks += 1

        # Check if article has URL
        if article.get('url') and article.get('url', '').startswith('http'):
            score += 1
            checks += 1
        else:
            checks += 1

        # Calculate quality score
        quality_score = score / checks if checks > 0 else 0

        return quality_score >= min_quality
